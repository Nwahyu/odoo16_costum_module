# Website.page ACL Verification Tests

This directory contains test scripts to verify that the ACL fix for portal users accessing the `website.page` model is working correctly.

## Background

The ACL fix was implemented to resolve an issue where portal users were getting stuck during login because they lacked write access to the `website.page` model. The security access rule `access_website_page_portal` was added via XML to grant portal users full access (read, write, create, unlink) to the `website.page` model.

The security rule is defined in [`vio_affiliate/security/website_page_security.xml`](../security/website_page_security.xml) and references:

- Model: `website.model_website_page`
- Group: `base.group_portal` (Portal users)
- Permissions: read, write, create, unlink all set to True

## Test Files

### 1. `test_website_page_acl.py`

Standard Odoo test class that can be run using Odoo's test framework.

**Features:**

- Test 1: Verifies the XML security file exists
- Test 2: Verifies the security access rule exists with correct permissions
- Test 3: Tests portal user write access to website.page model
- Test 4: Simulates portal user login process
- Test 5: Comprehensive verification of all permissions
- Test 6: Checks for conflicting ir.rules

**Usage:**

```bash
# Run all tests for vio_affiliate module
odoo-bin -c odoo.conf -d <database> --stop-after-init --test-enable --test-tags vio_affiliate

# Run specific test class
odoo-bin -c odoo.conf -d <database> --stop-after-init --test-enable --test-tags vio_affiliate.TestWebsitePageACL
```

### 2. `verify_acl_fix.py`

Standalone verification script that can be executed directly from Odoo shell or as a standalone script.

**Features:**

- Same comprehensive tests as test_website_page_acl.py
- Can be run without Odoo's test framework
- Provides detailed logging output
- Returns exit codes for CI/CD integration

**Usage:**

**Option 1: Run from Odoo shell**

```bash
# Start Odoo shell
odoo-bin shell -c odoo.conf -d <database>

# In the shell, execute:
exec(open('vio_affiliate/tests/verify_acl_fix.py').read())
```

**Option 2: Run as standalone script**

```bash
# This will work if Odoo environment is properly configured
python vio_affiliate/tests/verify_acl_fix.py
```

**Option 3: Import and run from Python**

```python
from vio_affiliate.tests.verify_acl_fix import verify_acl_fix

# In an Odoo environment with env available
results = verify_acl_fix(env)
print(f"Passed: {results['passed']}, Failed: {results['failed']}")
```

## Test Results

The tests verify the following:

1. **XML Security File Exists**: Confirms that the `website_page_security.xml` file is present in the security directory.

2. **Security Access Rule Exists**: Confirms that the `access_website_page_portal` rule is properly created in `ir.model.access` from the XML file.

3. **Portal User Write Access**: Verifies that portal users can:

   - Read from `website.page` model
   - Write to `website.page` model
   - Create records in `website.page` model
   - Delete records from `website.page` model

4. **Login Process**: Simulates the portal user login flow to ensure it doesn't get stuck when accessing `website.page` model.

5. **Permission Verification**: Comprehensive check of all permissions (read, write, create, unlink).

6. **Rule Conflicts**: Checks for any conflicting `ir.rule` records that might override the ACL permissions.

## Expected Output

When all tests pass, you should see output similar to:

```
================================================================================
WEBSITE.PAGE ACL VERIFICATION TEST
================================================================================

TEST 1: Checking if XML security file exists
--------------------------------------------------------------------------------
✓ PASS: XML security file 'website_page_security.xml' found
  - File path: /path/to/vio_affiliate/security/website_page_security.xml

TEST 2: Checking if security access rule exists
--------------------------------------------------------------------------------
✓ PASS: Security access rule 'access_website_page_portal' found
  - Rule ID: 123
  - Model: website.page
  - Model Reference: website.model_website_page
  - Group: Portal
  - Group Reference: base.group_portal
  - Read Permission: True
  - Write Permission: True
  - Create Permission: True
  - Unlink Permission: True

TEST 3: Verifying portal user write access to website.page
--------------------------------------------------------------------------------
✓ Created test website page: Test Page for ACL Verification (ID: 456)
✓ Created portal user: Test Portal User ACL (ID: 789)
✓ PASS: Portal user successfully wrote to website.page model
  - Page name updated to: Test Page - Modified by Portal User
✓ PASS: Portal user successfully read from website.page model
  - Number of pages read: 1
✓ PASS: Portal user successfully created website.page record
  - New page ID: 790

TEST 4: Verifying portal user login process
--------------------------------------------------------------------------------
✓ Using existing portal user: Test Portal User ACL
✓ PASS: Portal user successfully accessed their own data
  - User: Test Portal User ACL
  - Email: test_portal_acl@example.com
✓ PASS: Portal user successfully accessed website.page model
  - Found 1 page(s)
  - Sample page: Test Page - Modified by Portal User
✓ PASS: Portal user successfully wrote to website.page during login simulation

TEST 5: Checking for conflicting ir.rules
--------------------------------------------------------------------------------
Found 2 ir.rule(s) for website.page model
  - Rule: website.page multi-company
    Domain: ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    Groups: []
    Perms Read: True
    Perms Write: True
    Perms Create: True
    Perms Unlink: True
  - Rule: website.page published
    Domain: [('website_published', '=', True)]
    Groups: []
    Perms Read: True
    Perms Write: False
    Perms Create: False
    Perms Unlink: False
✓ PASS: No conflicting ir.rules found that would restrict portal users

================================================================================
TEST SUMMARY
================================================================================
Total Tests: 5
Passed: 5
Failed: 0

✓ XML security file exists: PASS
✓ Security access rule exists with correct permissions: PASS
✓ Portal user has write access to website.page: PASS
✓ Portal user login process works without getting stuck: PASS
✓ No conflicting ir.rules for portal users: PASS
================================================================================

ALL TESTS PASSED - ACL fix is working correctly
```

## Troubleshooting

### Tests Fail with "XML security file not found"

- Verify that the `website_page_security.xml` file exists in `vio_affiliate/security/` directory
- Check that the file is properly formatted XML
- Ensure the module's `__manifest__.py` includes the security file in the `data` section

### Tests Fail with "Access rule not found"

- Verify that the `access_website_page_portal` entry exists in `vio_affiliate/security/website_page_security.xml`
- Check that the XML file is properly formatted with correct model and group references
- Restart Odoo and update the module: `odoo-bin -c odoo.conf -d <database> -u vio_affiliate --stop-after-init`

### Tests Fail with "Portal user cannot write to website.page"

- Check that the portal group has the correct permissions in the access rule
- Verify there are no conflicting `ir.rule` records
- Check Odoo logs for detailed error messages

### Tests Fail with "Portal user login process failed"

- This may indicate the ACL fix is not working
- Check if there are other security rules affecting portal users
- Verify the portal user has the correct group assignments

## Security Considerations

The ACL fix grants portal users full access (read, write, create, unlink) to the `website.page` model. This is necessary for the affiliate module to function correctly, but you should:

1. Review your security requirements to ensure this level of access is acceptable
2. Consider implementing additional record-level rules if needed
3. Monitor portal user activity to ensure no abuse occurs

## Integration with CI/CD

The `verify_acl_fix.py` script returns exit codes that can be used in CI/CD pipelines:

- Exit code 0: All tests passed
- Exit code 1: One or more tests failed

Example for GitHub Actions:

```yaml
- name: Verify ACL Fix
  run: |
    odoo-bin shell -c odoo.conf -d ${{ secrets.DB_NAME }} < vio_affiliate/tests/verify_acl_fix.py
```

## Additional Resources

- Odoo Security Documentation: https://www.odoo.com/documentation/16.0/developer/reference/addons/security.html
- Odoo Testing Documentation: https://www.odoo.com/documentation/16.0/developer/reference/addons/tests.html
- XML Data Files Documentation: https://www.odoo.com/documentation/16.0/developer/reference/addons/data.html
