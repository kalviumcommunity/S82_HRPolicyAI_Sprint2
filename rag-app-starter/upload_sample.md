# Document Upload & Indexing — Sample Run

## Upload Request
```bash
curl -X POST http://localhost:8000/documents \
  -H "Authorization: Bearer <token>" \
  -F "file=@new-policy.md" \
  -F "name=Remote Work Policy" \
  -F "region=Global" \
  -F "category=Work Policy"
```

## Upload Response
```json
{
  "id": "doc_3a8f1c2d",
  "name": "Remote Work Policy",
  "filename": "new-policy.md",
  "region": "Global",
  "category": "Work Policy",
  "status": "Indexed",
  "chunkCount": 85,
  "fileSize": "0.1 MB",
  "fileUrl": "/documents/doc_3a8f1c2d/file"
}
```
> Indexing runs as a **background task** — the file is searchable within seconds of upload without restarting the server.

## Follow-up Query (proves runtime searchability)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the remote work policy?"}'
```

```json
{
  "answer": "According to the Remote Work Policy [1], employees may work remotely up to 3 days per week...",
  "sources": [
    { "source": "new-policy.md", "chunk_id": "new-policy_chunk_0", "score": null }
  ],
  "status": "answered"
}
```

## Error Handling
| Scenario | Status Code | Detail |
|---|---|---|
| Unsupported format (e.g. `.docx`) | `415` | Unsupported file type |
| Empty file | `400` | Uploaded file is empty |
| File > 20 MB | `413` | File exceeds 20 MB limit |
| Server/indexing error | `500` | Document indexing failed |
