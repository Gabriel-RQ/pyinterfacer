import unittest
import pygame

from pyinterfacer import interfacer as PyInterfacer


class TestPyInterfacer(unittest.TestCase):
    def setUp(self) -> None:
        # PyInterfacer requires a display surface when 'PyInterfacer.init' is called
        pygame.display.set_mode((1, 1))
        PyInterfacer.load("test_interface.yaml")
        PyInterfacer.init()
        PyInterfacer.go_to("test_interface")

    def tearDown(self) -> None:
        PyInterfacer.unload()

    def test_init(self) -> None:
        self.assertIsNotNone(PyInterfacer.display)
        self.assertTrue(len(PyInterfacer._PyInterfacer__interface_queue) == 0)
        self.assertTrue(len(PyInterfacer._interfaces) > 0)
        self.assertTrue(len(PyInterfacer._components) > 0)

    def test_backup_unload_reload(self) -> None:
        PyInterfacer.unload(backup=True)
        self.assertTrue(PyInterfacer.backup.have_backup)
        # Asserts PyInterfacer data is cleared
        self.assertIsNone(PyInterfacer.current_focus)
        self.assertTrue(
            all(
                (
                    len(PyInterfacer._interfaces) == 0,
                    len(PyInterfacer._components) == 0,
                    len(PyInterfacer._component_action_mapping) == 0,
                )
            )
        )
        # Asserts overlay data is cleared
        self.assertTrue(
            all(
                (
                    len(PyInterfacer.overlay._render_targets["single"]) == 0,
                    len(PyInterfacer.overlay._render_targets["many"]) == 0,
                    len(PyInterfacer.overlay._render_targets["interfaces"]) == 0,
                )
            )
        )

        # Actions and overlay may be empty, as they're optional features
        PyInterfacer.reload()
        self.assertFalse(PyInterfacer.backup.have_backup)
        self.assertTrue(
            all((len(PyInterfacer._interfaces) > 0, len(PyInterfacer._components) > 0))
        )

    def test_inject(self) -> None:
        # Inject an interface
        PyInterfacer.inject(
            {
                "interface": "injected-interface",
                "display": "default",
                "components": [
                    {
                        "type": "text",
                        "id": "injected-text",
                        "x": "50%",
                        "y": "50%",
                        "text": "Injected",
                    }
                ],
            }
        )

        self.assertIsNotNone(PyInterfacer.get_interface("injected-interface"))
        self.assertIsNotNone(PyInterfacer.get_component("injected-text"))

        # Inject a single component
        PyInterfacer.inject(
            {
                "type": "text",
                "id": "injected-text2",
                "x": "50%",
                "y": "50%",
                "text": "Injected",
            },
            "injected-interface",
        )

        self.assertIsNotNone(PyInterfacer.get_component("injected-text2"))


if __name__ == "__main__":
    unittest.main()
