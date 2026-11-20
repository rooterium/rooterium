# Optional Caddy snippets

Every `*.caddy` file in this directory is imported into the site block of
`deploy/Caddyfile`. Real snippets are server-specific and not committed
(see `.gitignore`).

## Example: Basic Auth (e.g. during a test phase)

```bash
docker compose -f compose.prod.yaml exec caddy caddy hash-password
# paste the hash into deploy/caddy.d/basic-auth.caddy:
```

```caddy
basic_auth {
	preview <hash>
}
```

Then reload: `docker compose -f compose.prod.yaml restart caddy`.
