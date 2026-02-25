# DeepSeek API Notes

## Required env var

- `DEEPSEEK_API_KEY`

## Default endpoint

- `https://api.deepseek.com/v1/chat/completions`

## Minimal request shape

```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "System prompt"},
    {"role": "user", "content": "User prompt"}
  ]
}
```

## Operational notes

- Keep transcript payload bounded (for example first 8k-12k chars) in the minimal version.
- For long transcripts, chunk first and merge summaries in a second pass.

