using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text.Json;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(CadAgent.NativeThinBackend.NativeThinBackendCommands))]

namespace CadAgent.NativeThinBackend;

public sealed class NativeThinBackendCommands
{
    private const string SchemaVersion = "native-thin-autocad-plugin-result/p13f/v1";
    private const string PreviewLayer = "CODEX_PREVIEW";

    [CommandMethod("CADAGENT_P13F_SPIKE", CommandFlags.Session)]
    public void RunP13FSpike()
    {
        string transactionId = Environment.GetEnvironmentVariable("CAD_AGENT_NATIVE_THIN_TRANSACTION_ID")
            ?? "tx-p13f-native-live-spike-001";
        string reportPath = Environment.GetEnvironmentVariable("CAD_AGENT_NATIVE_THIN_REPORT")
            ?? Path.Combine(Path.GetTempPath(), "native_thin_plugin_result.json");

        var report = BaseReport(transactionId);
        report["nativePluginInvoked"] = true;

        try
        {
            Document? document = Application.DocumentManager.MdiActiveDocument;
            if (document is null)
            {
                throw new InvalidOperationException("No active AutoCAD document is available.");
            }

            Database database = document.Database;
            report["documentStateBefore"] = DocumentState(document, database);
            var createdIds = new List<ObjectId>();
            var createdHandles = new List<string>();

            using (document.LockDocument())
            {
                EnsurePreviewLayer(database);
                using (Transaction transaction = database.TransactionManager.StartTransaction())
                {
                    var blockTable = (BlockTable)transaction.GetObject(database.BlockTableId, OpenMode.ForRead);
                    var modelSpace = (BlockTableRecord)transaction.GetObject(
                        blockTable[BlockTableRecord.ModelSpace],
                        OpenMode.ForWrite);

                    var polyline = new Polyline(4)
                    {
                        Closed = true,
                    };
                    polyline.SetDatabaseDefaults(database);
                    polyline.Layer = PreviewLayer;
                    polyline.AddVertexAt(0, new Point2d(100.0, 200.0), 0.0, 0.0, 0.0);
                    polyline.AddVertexAt(1, new Point2d(1300.0, 200.0), 0.0, 0.0, 0.0);
                    polyline.AddVertexAt(2, new Point2d(1300.0, 800.0), 0.0, 0.0, 0.0);
                    polyline.AddVertexAt(3, new Point2d(100.0, 800.0), 0.0, 0.0, 0.0);

                    ObjectId objectId = modelSpace.AppendEntity(polyline);
                    transaction.AddNewlyCreatedDBObject(polyline, true);
                    createdIds.Add(objectId);
                    createdHandles.Add(polyline.Handle.ToString());
                    transaction.Commit();
                }

                var readbackEntities = ReadbackCreatedEntities(database, createdIds);
                bool bboxLayerEntityVerified = readbackEntities.Count == createdIds.Count && readbackEntities.TrueForAll(
                    entity => string.Equals(Convert.ToString(entity["layer"], CultureInfo.InvariantCulture), PreviewLayer, StringComparison.Ordinal));

                bool rolledBack = RollbackCreatedEntities(database, createdIds);

                report["status"] = rolledBack && bboxLayerEntityVerified ? "geometry_verified" : "not_verified";
                report["verificationStatus"] = rolledBack && bboxLayerEntityVerified ? "verified" : "not_verified";
                report["cadWritesAttempted"] = true;
                report["committedPreview"] = true;
                report["createdHandles"] = createdHandles;
                report["createdHandlesReadback"] = new Dictionary<string, object?>
                {
                    ["status"] = bboxLayerEntityVerified ? "verified" : "not_verified",
                    ["readbackStatus"] = bboxLayerEntityVerified ? "verified" : "not_verified",
                    ["createdHandles"] = createdHandles,
                    ["entities"] = readbackEntities,
                };
                report["bboxLayerEntityAudit"] = new Dictionary<string, object?>
                {
                    ["status"] = bboxLayerEntityVerified ? "verified" : "not_verified",
                    ["bboxChecked"] = readbackEntities.TrueForAll(entity => entity.ContainsKey("bbox")),
                    ["layerChecked"] = readbackEntities.TrueForAll(entity => string.Equals(Convert.ToString(entity["layer"], CultureInfo.InvariantCulture), PreviewLayer, StringComparison.Ordinal)),
                    ["entityAuditChecked"] = readbackEntities.Count == createdIds.Count,
                    ["targetLayer"] = PreviewLayer,
                };
                report["rollbackStatus"] = rolledBack ? "rolled_back" : "rollback_failed";
                report["rollbackProof"] = new Dictionary<string, object?>
                {
                    ["status"] = rolledBack ? "verified" : "not_verified",
                    ["rollbackRequired"] = true,
                    ["rollbackStatus"] = rolledBack ? "rolled_back" : "rollback_failed",
                    ["verified"] = rolledBack,
                    ["rolledBackHandles"] = createdHandles,
                };
                report["documentState"] = rolledBack ? "rolled_back_no_save" : "rollback_failed_no_save";
                report["documentStateAfter"] = DocumentState(document, database);
                report["blockingReasons"] = rolledBack && bboxLayerEntityVerified
                    ? Array.Empty<string>()
                    : new[] { "native_thin_live_spike_proof_not_verified" };
                report["missingEvidence"] = rolledBack && bboxLayerEntityVerified
                    ? Array.Empty<string>()
                    : new[] { "real_cad_readback", "native_thin_rollback_proof" };
            }
        }
        catch (System.Exception exception)
        {
            report["status"] = "external_blocker";
            report["verificationStatus"] = "not_verified";
            report["cadWritesAttempted"] = false;
            report["blockingReasons"] = new[] { "native_thin_plugin_exception:" + exception.GetType().Name + ":" + exception.Message };
            report["missingEvidence"] = new[] { "real_cad_readback", "native_thin_rollback_proof", "no_save_guard" };
            report["documentState"] = "plugin_exception_no_save";
            report["documentStateAfter"] = "plugin_exception_no_save";
        }
        finally
        {
            report["savedCurrentDwg"] = false;
            report["noSaveAudit"] = new Dictionary<string, object?>
            {
                ["status"] = "verified",
                ["saveAttempted"] = false,
                ["saveAllowed"] = false,
                ["savedCurrentDwg"] = false,
            };
            WriteReport(reportPath, report);
        }
    }

    private static Dictionary<string, object?> BaseReport(string transactionId)
    {
        return new Dictionary<string, object?>
        {
            ["schemaVersion"] = SchemaVersion,
            ["status"] = "not_verified",
            ["verificationStatus"] = "not_verified",
            ["backend"] = "autocad_plugin",
            ["targetLayer"] = PreviewLayer,
            ["transactionId"] = transactionId,
            ["nativePluginInvoked"] = false,
            ["cadWritesAttempted"] = false,
            ["savedCurrentDwg"] = false,
            ["committedPreview"] = false,
            ["createdHandles"] = Array.Empty<string>(),
            ["createdHandlesReadback"] = new Dictionary<string, object?>
            {
                ["status"] = "not_run",
                ["entities"] = Array.Empty<object>(),
            },
            ["bboxLayerEntityAudit"] = new Dictionary<string, object?>
            {
                ["status"] = "not_run",
                ["bboxChecked"] = false,
                ["layerChecked"] = false,
                ["entityAuditChecked"] = false,
                ["targetLayer"] = PreviewLayer,
            },
            ["rollbackRequired"] = true,
            ["rollbackStatus"] = "not_started",
            ["rollbackProof"] = new Dictionary<string, object?>
            {
                ["status"] = "not_run",
                ["rollbackRequired"] = true,
                ["rollbackStatus"] = "not_started",
                ["verified"] = false,
            },
            ["noSaveAudit"] = new Dictionary<string, object?>
            {
                ["status"] = "not_run",
                ["saveAttempted"] = false,
                ["saveAllowed"] = false,
                ["savedCurrentDwg"] = false,
            },
            ["documentStateBefore"] = "",
            ["documentState"] = "",
            ["documentStateAfter"] = "",
            ["blockingReasons"] = Array.Empty<string>(),
            ["missingEvidence"] = Array.Empty<string>(),
            ["artifacts"] = new Dictionary<string, object?>(),
        };
    }

    private static void EnsurePreviewLayer(Database database)
    {
        using Transaction transaction = database.TransactionManager.StartTransaction();
        var layerTable = (LayerTable)transaction.GetObject(database.LayerTableId, OpenMode.ForRead);
        if (!layerTable.Has(PreviewLayer))
        {
            layerTable.UpgradeOpen();
            var layerRecord = new LayerTableRecord { Name = PreviewLayer };
            layerTable.Add(layerRecord);
            transaction.AddNewlyCreatedDBObject(layerRecord, true);
        }

        transaction.Commit();
    }

    private static List<Dictionary<string, object?>> ReadbackCreatedEntities(Database database, List<ObjectId> objectIds)
    {
        var entities = new List<Dictionary<string, object?>>();
        using Transaction transaction = database.TransactionManager.StartTransaction();
        foreach (ObjectId objectId in objectIds)
        {
            var entity = (Entity)transaction.GetObject(objectId, OpenMode.ForRead);
            Extents3d extents = entity.GeometricExtents;
            entities.Add(new Dictionary<string, object?>
            {
                ["handle"] = entity.Handle.ToString(),
                ["type"] = entity.GetRXClass().DxfName,
                ["layer"] = entity.Layer,
                ["bbox"] = new Dictionary<string, object?>
                {
                    ["min"] = new[] { extents.MinPoint.X, extents.MinPoint.Y, extents.MinPoint.Z },
                    ["max"] = new[] { extents.MaxPoint.X, extents.MaxPoint.Y, extents.MaxPoint.Z },
                },
            });
        }

        transaction.Commit();
        return entities;
    }

    private static bool RollbackCreatedEntities(Database database, List<ObjectId> objectIds)
    {
        using (Transaction transaction = database.TransactionManager.StartTransaction())
        {
            foreach (ObjectId objectId in objectIds)
            {
                var entity = (Entity)transaction.GetObject(objectId, OpenMode.ForWrite, false);
                entity.Erase();
            }

            transaction.Commit();
        }

        using Transaction verifyTransaction = database.TransactionManager.StartTransaction();
        foreach (ObjectId objectId in objectIds)
        {
            var dbObject = verifyTransaction.GetObject(objectId, OpenMode.ForRead, true);
            if (!dbObject.IsErased)
            {
                return false;
            }
        }

        verifyTransaction.Commit();
        return true;
    }

    private static string DocumentState(Document document, Database database)
    {
        string name = string.IsNullOrWhiteSpace(document.Name) ? "unnamed_document" : document.Name;
        return name + "|tilemode=" + database.TileMode.ToString(CultureInfo.InvariantCulture);
    }

    private static void WriteReport(string reportPath, Dictionary<string, object?> report)
    {
        string? directory = Path.GetDirectoryName(reportPath);
        if (!string.IsNullOrWhiteSpace(directory))
        {
            Directory.CreateDirectory(directory);
        }

        var options = new JsonSerializerOptions { WriteIndented = true };
        File.WriteAllText(reportPath, JsonSerializer.Serialize(report, options));
    }
}
