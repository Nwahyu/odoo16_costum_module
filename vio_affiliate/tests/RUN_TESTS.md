# Quick Guide: Running ACL Verification Tests

## Quick Start

### Option 1: Run from Odoo Shell (Recommended)

```bash
# Start Odoo shell
odoo-bin shell -c odoo.conf -d your_database

# In the shell, execute:
exec(open('vio_affiliate/tests/verify_acl_fix.py').read())
```

### Option 2: Run Standard Odoo Tests

```bash
# Run all tests for vio_affiliate module
odoo-bin -c odoo.conf -d your_database --stop-after-init --test-enable --test-tags vio_affiliate
```

### Option 3: Run Specific Test Class

```bash
# Run only the ACL tests
odoo-bin -c odoo.conf -d your_database --stop-after-init --test-enable --test-tags vio_affiliate.TestWebsitePageACL
```

## What the Tests Do

1. **Check Security Access Rule**: Verifies `access_website_page_portal` exists in `ir.model.access`
2. **Test Portal User Write Access**: Confirms portal users can read/write/create/delete website.page records
3. **Simulate Login Process**: Tests the login flow that was previously failing
4. **Check for Conflicts**: Ensures no conflicting ir.rules override the ACL

## Expected Results

✅ All tests pass = ACL fix is working correctly
❌ Any test fails = ACL fix needs review

## Troubleshooting

**Tests fail?**

1. Update the module: `odoo-bin -c odoo.conf -d your_database -u vio_affiliate --stop-after-init`
2. Check `vio_affiliate/security/ir.model.access.csv` has the `access_website_page_portal` entry
3. Review Odoo logs for detailed error messages

**Need more details?**
See `README.md` for comprehensive documentation.
