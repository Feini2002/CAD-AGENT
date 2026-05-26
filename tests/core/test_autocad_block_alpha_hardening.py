from __future__ import annotations

import unittest

from core.cad_io.autocad_com import (
    CONTROLLED_BLOCK_NAME,
    PREVIEW_LAYER,
    BlockAlphaInsertionError,
)
from tests.core.test_autocad_com_driver import ControlledBlockDefinitionTests


def _helper() -> ControlledBlockDefinitionTests:
    return ControlledBlockDefinitionTests("test_block_definition_failure_payload_is_structured")


class AutoCADBlockAlphaHardeningTests(unittest.TestCase):
    def test_ensure_controlled_block_definition_rejects_invalid_existing_shape(self) -> None:
        driver = _helper()._driver_with_blocks(existing={CONTROLLED_BLOCK_NAME}, invalid_existing_definition=True)
        result = driver.ensure_controlled_block_definition()
        self.assertEqual(result["status"], "definition_missing")
        self.assertEqual(result["failure_category"], "definition_mismatch")
        self.assertEqual(driver.doc.Blocks.created, [])

    def test_ensure_controlled_block_definition_rolls_back_partial_definition(self) -> None:
        driver = _helper()._driver_with_blocks(add_line_raises=RuntimeError("line failed"))
        result = driver.ensure_controlled_block_definition()
        self.assertEqual(result["status"], "definition_missing")
        assert driver.doc.Blocks.last_record is not None
        self.assertTrue(driver.doc.Blocks.last_record.deleted)

    def test_insert_block_alpha_rejects_attributes_before_definition_write(self) -> None:
        driver = _helper()._driver_with_insert_block()
        with self.assertRaisesRegex(BlockAlphaInsertionError, "attributes"):
            driver.insert_block_alpha(
                block_id="controlled-test-block-001",
                block_name=CONTROLLED_BLOCK_NAME,
                base_point=[0, 0, 0],
                layer=PREVIEW_LAYER,
                attributes={"TAG": "VALUE"},
            )
        self.assertEqual(driver.doc.Blocks.created, [])
        self.assertEqual(driver.model_space.insert_calls, [])

    def test_insert_block_alpha_rejects_invalid_base_point_before_definition_write(self) -> None:
        driver = _helper()._driver_with_insert_block()
        with self.assertRaisesRegex(ValueError, "base_point"):
            driver.insert_block_alpha(
                block_id="controlled-test-block-001",
                block_name=CONTROLLED_BLOCK_NAME,
                base_point=["bad", 0, 0],
                layer=PREVIEW_LAYER,
            )
        self.assertEqual(driver.doc.Blocks.created, [])
        self.assertEqual(driver.model_space.insert_calls, [])

    def test_insert_block_alpha_rolls_back_reference_when_handle_missing(self) -> None:
        driver = _helper()._driver_with_insert_block(existing={CONTROLLED_BLOCK_NAME})
        inserted: list[object] = []

        class FakeBlockReference:
            Handle = ""

            def __init__(self) -> None:
                self.deleted = False

            def Delete(self) -> None:
                self.deleted = True

        def insert_without_handle(*_args: object) -> FakeBlockReference:
            entity = FakeBlockReference()
            inserted.append(entity)
            return entity

        driver.model_space.InsertBlock = insert_without_handle  # type: ignore[method-assign]
        with self.assertRaises(BlockAlphaInsertionError):
            driver.insert_block_alpha(
                block_id="controlled-test-block-001",
                block_name=CONTROLLED_BLOCK_NAME,
                base_point=[0, 0, 0],
                layer=PREVIEW_LAYER,
            )
        self.assertTrue(getattr(inserted[0], "deleted"))


if __name__ == "__main__":
    unittest.main()
