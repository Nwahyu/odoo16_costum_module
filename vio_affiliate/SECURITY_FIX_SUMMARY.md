# Security Access Rule Fix Summary

## Problem

The module was failing to load with the following error:

```
No matching record found for external id 'model_website_page' in field 'Model'
Missing required value for the field 'Model' (model_id)
```

## Root Cause

The security access rule in [`vio_affiliate/security/ir.model.access.csv`](vio_affiliate/security/ir.model.access.csv:7) was trying to reference the `website.page` model using an incorrect external ID format:

```csv
access_website_page_portal,access_website_page_portal,model_website_page,base.group_portal,1,1,1,1
```

The issue was that `model_website_page` is not a valid external ID reference. This external ID doesn't exist because:

1. The `website.page` model belongs to the `website` module, not `vio_affiliate`
2. In Odoo CSV security files, you can only reference models defined in the same module
3. To reference models from other modules, you need to use the full external ID format: `module_name.model_model_name`

## Solution

The fix involved two changes:

### 1. Removed the problematic line from CSV

Removed the invalid reference from [`vio_affiliate/security/ir.model.access.csv`](vio_affiliate/security/ir.model.access.csv:7):

```csv
# REMOVED: access_website_page_portal,access_website_page_portal,model_website_page,base.group_portal,1,1,1,1
```

### 2. Created proper XML security rule

Created a new file [`vio_affiliate/security/website_page_security.xml`](vio_affiliate/security/website_page_security.xml:1) with the correct external ID reference:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Security access rule for website.page model for portal users -->
    <record id="access_website_page_portal" model="ir.model.access">
        <field name="name">access_website_page_portal</field>
        <field name="model_id" ref="website.model_website_page"/>
        <field name="group_id" ref="base.group_portal"/>
        <field name="perm_read" eval="1"/>
        <field name="perm_write" eval="1"/>
        <field name="perm_create" eval="1"/>
        <field name="perm_unlink" eval="1"/>
    </record>
</odoo>
```

### 3. Updated module manifest

Added the new security XML file to [`vio_affiliate/__manifest__.py`](vio_affiliate/__manifest__.py:15):

```python
'data': [
    'security/ir.model.access.csv',
    'security/website_page_security.xml',  # NEW
    # ... rest of data files
],
```

## Key Points

1. **CSV vs XML for Security Rules**:

   - CSV files (`ir.model.access.csv`) are best for models defined within the same module
   - XML files are required when referencing models from other modules

2. **External ID Format**:

   - For models in the same module: `model_<model_name>`
   - For models in other modules: `<module_name>.model_<model_name>`

3. **Module Dependencies**:
   - The [`vio_affiliate/__manifest__.py`](vio_affiliate/__manifest__.py:10) already correctly depends on `website` module
   - This ensures the `website.model_website_page` external ID is available when the security rule is loaded

## Verification

The fix can be verified by:

1. Updating the module: `odoo-bin -u vio_affiliate -d <database>`
2. Running the test suite in [`vio_affiliate/tests/test_website_page_acl.py`](vio_affiliate/tests/test_website_page_acl.py:1)
3. Checking that portal users can now access the `website.page` model without errors

## Files Modified

- [`vio_affiliate/security/ir.model.access.csv`](vio_affiliate/security/ir.model.access.csv:1) - Removed invalid line
- [`vio_affiliate/__manifest__.py`](vio_affiliate/__manifest__.py:1) - Added new security XML reference

## Files Created

- [`vio_affiliate/security/website_page_security.xml`](vio_affiliate/security/website_page_security.xml:1) - New security rule file
- [`vio_affiliate/SECURITY_FIX_SUMMARY.md`](vio_affiliate/SECURITY_FIX_SUMMARY.md:1) - This documentation
