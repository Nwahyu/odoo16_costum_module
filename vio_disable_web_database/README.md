# Vio Disable Web Database

## What It Does

This Odoo module blocks access to all `/web/database/*` endpoints (database manager, backup, etc.) by redirecting requests to `/web/login`. It provides an **authorized backup bypass** that allows trusted clients to download database backups via a secret HTTP header.

---

## Ringkasan (Indonesian)

Modul ini memblokir akses ke endpoint `/web/database/*` agar pengguna tidak dapat mengakses database manager Odoo dari browser. Modul juga menyediakan bypass khusus untuk backup database melalui header HTTP rahasia.

---

## Installation

### Via Odoo UI

1. Copy the `vio_disable_web_database` folder into your Odoo addons path.
2. Restart the Odoo service.
3. Go to **Apps → Update Apps List** and confirm.
4. Search for **"Vio Disable Web Database"** and click **Install**.

### Via CLI

```bash
venv/scripts/python odoo-bin -c odoo.conf -d DB_NAME -i vio_disable_web_database --stop-after-init
```

Replace `DB_NAME` with the name of your target database.

---

## Usage

Once installed, the module automatically intercepts all requests to:

- `/web/database`
- `/web/database/manager`
- `/web/database/backup`
- `/web/database/manager/backup`

All requests are redirected to `/web/login` by default.

---

## Authorized Backup Bypass

To allow a trusted client to download a database backup, send a request with the special header:

```
X-name-header: 04julidarsana
```

### curl Example

```bash
curl -X POST \
  -H "X-name-header: 04julidarsana" \
  -d "master_pwd=YOUR_MASTER_PASSWORD&name=DB_NAME&backup_format=zip" \
  -o backup.zip \
  https://your-odoo-server.com/web/database/backup
```

Replace:

- `YOUR_MASTER_PASSWORD` — your Odoo master/admin password.
- `DB_NAME` — the database name to back up.
- `https://your-odoo-server.com` — your Odoo instance URL.

### ⚠️ Security Note

> **Only send the `X-name-header` from trusted hosts and networks.** Do not expose this header value in client-side code, public scripts, or untrusted environments. Consider restricting access at the reverse-proxy level (e.g., Nginx) to specific IP addresses for the backup endpoint.

---

## License

LGPL-3
