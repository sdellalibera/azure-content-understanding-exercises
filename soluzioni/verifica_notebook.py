"""Verifica locale del laboratorio: nessuna credenziale o chiamata Azure reale."""

import ast
from contextlib import nullcontext, redirect_stdout
from copy import deepcopy
import inspect
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

import nbformat
from agent_framework import BaseChatClient, ChatResponse, Content, Message
from azure.ai.contentunderstanding.models import AnalysisResult, ContentAnalyzer


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "soluzioni").glob("[0-9][0-9]-*.ipynb"))
CELL_PATTERN = re.compile(r"<!-- cell:([\w-]+) -->\n```python\n(.*?)\n```", re.S)
FIXTURE = {
    "analyzerId": "hotel-bill-mario-rossi-v1",
    "apiVersion": "2026-06-01-preview",
    "contents": [{
        "kind": "document",
        "mimeType": "application/pdf",
        "startPageNumber": 1,
        "endPageNumber": 2,
        "markdown": "# Conto sintetico per test\nOspite: Mario Rossi\nSaldo: 0.00",
        "fields": {
            "Ospite": {"type": "string", "valueString": "Mario Rossi"},
            "Saldo": {"type": "number", "valueNumber": 0},
        },
    }],
}


def sample_sources():
    return {
        (path.name, match[1]): match[2]
        for path in (ROOT / "esercizi").glob("[0-9][0-9]-*.md")
        for match in CELL_PATTERN.finditer(path.read_text(encoding="utf-8"))
    }


async def execute_notebook(path, namespace=None):
    namespace = {} if namespace is None else namespace
    for cell in nbformat.read(path, as_version=4).cells:
        if cell.cell_type != "code":
            continue
        code = compile(
            cell.source, f"{path.name}:{cell.id}", "exec",
            flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
        )
        result = eval(code, namespace)
        if inspect.isawaitable(result):
            await result
    return namespace


class RecordingChatClient(BaseChatClient):
    """Esegue il vero pipeline MAF senza inferenza di rete."""

    def __init__(self):
        super().__init__()
        self.client = nullcontext()
        self.calls = []

    async def _inner_get_response(self, *, messages, stream, options, **kwargs):
        if stream:
            raise AssertionError("Il laboratorio non richiede streaming.")
        self.calls.append(list(messages))
        return ChatResponse(messages=[
            Message(role="assistant", contents=[Content.from_text("Risposta offline di test.")])
        ])


class LaboratoryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "esercizi" / "documenti").mkdir(parents=True)
        (self.root / "soluzioni").mkdir()
        (self.root / ".env.example").write_text("# test", encoding="utf-8")
        (self.root / ".env").write_text(
            "AZURE_CONTENTUNDERSTANDING_ENDPOINT=https://cu.invalid/\n"
            "AZURE_CONTENTUNDERSTANDING_API_KEY=offline-test-key\n"
            "DOCUMENT_PATH=esercizi/documenti/test.pdf\n"
            "FOUNDRY_PROJECT_ENDPOINT=https://cu.invalid/api/projects/test\n"
            "FOUNDRY_MODEL=offline-deployment\n",
            encoding="utf-8",
        )
        (self.root / "esercizi" / "documenti" / "test.pdf").write_bytes(
            b"%PDF-1.4\n% Synthetic offline input, never sent to a service."
        )
        template = (ROOT / "esercizi" / "analyzer-template.json").read_text(encoding="utf-8")
        (self.root / "esercizi" / "analyzer-template.json").write_text(template, encoding="utf-8")
        self.analyzer = ContentAnalyzer(json.loads(template))
        self.cwd = Path.cwd()
        os.chdir(self.root)
        self.environment = patch.dict(os.environ)
        self.environment.start()
        self.console = io.StringIO()
        self.stdout = redirect_stdout(self.console)
        self.stdout.__enter__()

    def tearDown(self):
        self.stdout.__exit__(None, None, None)
        self.environment.stop()
        os.chdir(self.cwd)
        self.temporary.cleanup()

    def test_notebook_format_and_samples(self):
        self.assertEqual(len(NOTEBOOKS), 6)
        sources = sample_sources()
        for path in NOTEBOOKS:
            notebook = nbformat.read(path, as_version=4)
            nbformat.validate(notebook)
            for cell in notebook.cells:
                if cell.cell_type == "code":
                    self.assertEqual(cell.outputs, [])
                    self.assertIsNone(cell.execution_count)
                    self.assertEqual(
                        cell.source,
                        sources[(cell.metadata.exercise, cell.metadata.sample)],
                    )
                    compile(cell.source, str(path), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)

    async def prepare_analyzer(self):
        selection = self.root / "soluzioni" / "output" / "analyzer-selection.json"
        selection.parent.mkdir(exist_ok=True)
        selection.write_text(json.dumps({
            "analyzer_id": "hotel-bill-mario-rossi-v1", "endpoint": "https://cu.invalid",
        }), encoding="utf-8")

    async def test_actual_agent_construction_without_network(self):
        await self.prepare_analyzer()
        # Si costruiscono i client reali, ma nessun token o risposta viene richiesto.
        namespace = await execute_notebook(NOTEBOOKS[4])
        self.assertEqual(namespace["agent"].name, "HotelBillAssistant")
        self.assertEqual(namespace["provider"].analyzer_id, "hotel-bill-mario-rossi-v1")
        self.assertTrue(namespace["agent"].client.client.is_closed())

    async def test_complete_path_with_real_provider_and_fake_services(self):
        recording_chat = RecordingChatClient()
        poller = AsyncMock()
        poller.result.return_value = AnalysisResult(deepcopy(FIXTURE))
        with (
            patch("azure.ai.contentunderstanding.ContentUnderstandingClient", autospec=True) as sdk,
            patch(
                "azure.ai.contentunderstanding.aio.ContentUnderstandingClient.begin_analyze_binary",
                new_callable=AsyncMock,
                return_value=poller,
            ) as analyze_async,
            patch("agent_framework.foundry.FoundryChatClient", return_value=recording_chat),
        ):
            client = sdk.return_value.__enter__.return_value
            client.get_analyzer.return_value = self.analyzer
            client.begin_analyze_binary.return_value.result.return_value = AnalysisResult(deepcopy(FIXTURE))
            namespaces = [await execute_notebook(path) for path in NOTEBOOKS]
            client.begin_create_analyzer.assert_called_once()
            self.assertFalse(client.begin_create_analyzer.call_args.kwargs["allow_replace"])
            client.begin_analyze_binary.assert_called_once()
            analyze_async.assert_awaited_once()
            self.assertEqual(analyze_async.call_args.kwargs["content_type"], "application/pdf")
            self.assertEqual(len(recording_chat.calls), 2)
            for messages in recording_chat.calls:
                rendered = "\n".join(message.text for message in messages)
                self.assertIn("Mario Rossi", rendered)
                self.assertIn("Saldo", rendered)
                self.assertFalse(any(c.type == "data" for m in messages for c in m.contents))

            output = self.root / "soluzioni" / "output"
            for filename in (
                "analyzer.json", "analyzer-selection.json", "analisi.json",
                "analisi-input.json", "contesto-llm.md", "contesto-provider.md",
            ):
                self.assertTrue((output / filename).is_file(), filename)
            self.assertIn("Mario Rossi", namespaces[3]["llm_text"])
            self.assertNotIn("# Conto sintetico", namespaces[3]["fields_only"])
            self.assertNotIn("fields:", namespaces[3]["markdown_only"])

            # Il percorso portale recupera lo stesso analyzer senza crearlo.
            sources = sample_sources()
            namespace = namespaces[1]
            namespace["MODALITA"] = "portale"
            client.begin_create_analyzer.reset_mock()
            exec(sources[("02-analyzer.md", "create")], namespace)
            client.begin_create_analyzer.assert_not_called()

            # Un documento modificato non puo riutilizzare l'analisi precedente.
            (self.root / "esercizi" / "documenti" / "test.pdf").write_bytes(b"%PDF-1.4\nchanged")
            with self.assertRaisesRegex(ValueError, "cambiato"):
                await execute_notebook(NOTEBOOKS[3])

    async def test_provider_failure_is_not_reported_as_success(self):
        await self.prepare_analyzer()
        poller = AsyncMock()
        poller.result.side_effect = RuntimeError("CU offline intenzionale")
        with (
            patch(
                "azure.ai.contentunderstanding.aio.ContentUnderstandingClient.begin_analyze_binary",
                new_callable=AsyncMock,
                return_value=poller,
            ),
            patch("agent_framework.foundry.FoundryChatClient", return_value=RecordingChatClient()),
            self.assertLogs("agent_framework.azure_contentunderstanding", level="WARNING"),
        ):
            with self.assertRaisesRegex(RuntimeError, "Analisi CU non riuscita"):
                await execute_notebook(NOTEBOOKS[5])
        self.assertNotIn("Risposta primo turno", self.console.getvalue())

    async def test_missing_inputs_fail_explicitly(self):
        with self.assertRaisesRegex(FileNotFoundError, "esercizio 2"):
            await execute_notebook(NOTEBOOKS[2])
        await self.prepare_analyzer()
        (self.root / "esercizi" / "documenti" / "test.pdf").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "Documento non trovato"):
            await execute_notebook(NOTEBOOKS[2])
        (self.root / ".env").write_text(
            "AZURE_CONTENTUNDERSTANDING_API_KEY=<inserire-key>\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "API_KEY"):
            await execute_notebook(NOTEBOOKS[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
