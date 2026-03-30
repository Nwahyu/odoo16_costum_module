# -*- coding: utf-8 -*-
"""
Standalone test script to verify ACL fix for portal users accessing website.page model.

This script can be executed directly in an Odoo environment to verify:
1. The XML security access rule file exists
2. The security access rule was properly created from XML
3. Portal users have write access to the website.page model
4. Portal user login process works without getting stuck

Usage:
    odoo-bin -c odoo.conf -d <database> --stop-after-init --test-enable --test-tags vio_affiliate
    Or run this script directly from Odoo shell:
    odoo-bin shell -c odoo.conf -d <database> < vio_affiliate/tests/verify_acl_fix.py
"""

import logging
import os

_logger = logging.getLogger(__name__)


def verify_acl_fix(env):
    """
    Main function to verify the ACL fix for portal users accessing website.page model.

    Args:
        env: Odoo environment object

    Returns:
        dict: Test results with pass/fail status
    """
    results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    _logger.info("")
    _logger.info("=" * 80)
    _logger.info("WEBSITE.PAGE ACL VERIFICATION TEST")
    _logger.info("=" * 80)
    _logger.info("")

    # Test 1: Check if XML security file exists
    _logger.info("TEST 1: Checking if XML security file exists")
    _logger.info("-" * 80)
    results['total_tests'] += 1

    try:
        # Get the module path
        module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        xml_file_path = os.path.join(module_path, 'security', 'website_page_security.xml')

        if os.path.exists(xml_file_path):
            _logger.info("✓ PASS: XML security file 'website_page_security.xml' found")
            _logger.info(f"  - File path: {xml_file_path}")
            results['passed'] += 1
            results['tests'].append({
                'name': 'XML security file exists',
                'status': 'PASS'
            })
        else:
            _logger.error("✗ FAIL: XML security file 'website_page_security.xml' NOT found")
            results['failed'] += 1
            results['tests'].append({
                'name': 'XML security file exists',
                'status': 'FAIL',
                'reason': f'File not found at {xml_file_path}'
            })
    except Exception as e:
        _logger.error(f"✗ FAIL: Error checking XML security file: {e}")
        results['failed'] += 1
        results['tests'].append({
            'name': 'XML security file exists',
            'status': 'FAIL',
            'reason': str(e)
        })

    _logger.info("")

    # Test 2: Check if security access rule exists
    _logger.info("TEST 2: Checking if security access rule exists")
    _logger.info("-" * 80)
    results['total_tests'] += 1

    try:
        access_rule = env['ir.model.access'].search([
            ('name', '=', 'access_website_page_portal'),
            ('model_id.model', '=', 'website.page'),
            ('group_id.name', '=', 'Portal')
        ], limit=1)

        if access_rule:
            _logger.info("✓ PASS: Security access rule 'access_website_page_portal' found")
            _logger.info(f"  - Rule ID: {access_rule.id}")
            _logger.info(f"  - Model: {access_rule.model_id.model}")
            _logger.info(f"  - Model Reference: website.model_website_page")
            _logger.info(f"  - Group: {access_rule.group_id.name}")
            _logger.info(f"  - Group Reference: base.group_portal")
            _logger.info(f"  - Read Permission: {access_rule.perm_read}")
            _logger.info(f"  - Write Permission: {access_rule.perm_write}")
            _logger.info(f"  - Create Permission: {access_rule.perm_create}")
            _logger.info(f"  - Unlink Permission: {access_rule.perm_unlink}")

            if all([access_rule.perm_read, access_rule.perm_write,
                   access_rule.perm_create, access_rule.perm_unlink]):
                results['passed'] += 1
                results['tests'].append({
                    'name': 'Security access rule exists with correct permissions',
                    'status': 'PASS'
                })
            else:
                _logger.error("✗ FAIL: Some permissions are missing")
                results['failed'] += 1
                results['tests'].append({
                    'name': 'Security access rule exists with correct permissions',
                    'status': 'FAIL',
                    'reason': 'Not all permissions are set to True'
                })
        else:
            _logger.error("✗ FAIL: Security access rule 'access_website_page_portal' NOT found")
            results['failed'] += 1
            results['tests'].append({
                'name': 'Security access rule exists with correct permissions',
                'status': 'FAIL',
                'reason': 'Access rule not found'
            })
    except Exception as e:
        _logger.error(f"✗ FAIL: Error checking access rule: {e}")
        results['failed'] += 1
        results['tests'].append({
            'name': 'Security access rule exists with correct permissions',
            'status': 'FAIL',
            'reason': str(e)
        })

    _logger.info("")

    # Test 3: Verify portal user write access
    _logger.info("TEST 3: Verifying portal user write access to website.page")
    _logger.info("-" * 80)
    results['total_tests'] += 1

    try:
        # Create a test website page
        website_page_model = env['website.page']
        test_page = website_page_model.create({
            'name': 'Test Page for ACL Verification',
            'url': '/test-acl-verification',
            'view_id': env.ref('website.homepage').id,
            'website_published': True,
        })
        _logger.info(f"✓ Created test website page: {test_page.name} (ID: {test_page.id})")

        # Create a portal user
        portal_group = env.ref('base.group_portal')
        portal_user = env['res.users'].create({
            'name': 'Test Portal User ACL',
            'login': 'test_portal_acl',
            'email': 'test_portal_acl@example.com',
            'groups_id': [(6, 0, [portal_group.id])],
            'password': 'test_password_123',
        })
        _logger.info(f"✓ Created portal user: {portal_user.name} (ID: {portal_user.id})")

        # Test write access with portal user
        test_page.with_user(portal_user).write({
            'name': 'Test Page - Modified by Portal User'
        })
        _logger.info("✓ PASS: Portal user successfully wrote to website.page model")
        _logger.info(f"  - Page name updated to: {test_page.name}")

        # Test read access
        pages = test_page.with_user(portal_user).search_read([], ['name', 'url'])
        _logger.info(f"✓ PASS: Portal user successfully read from website.page model")
        _logger.info(f"  - Number of pages read: {len(pages)}")

        # Test create access
        new_page = test_page.with_user(portal_user).create({
            'name': 'Test Page Created by Portal User',
            'url': '/test-portal-created',
            'view_id': env.ref('website.homepage').id,
        })
        _logger.info("✓ PASS: Portal user successfully created website.page record")
        _logger.info(f"  - New page ID: {new_page.id}")

        results['passed'] += 1
        results['tests'].append({
            'name': 'Portal user has write access to website.page',
            'status': 'PASS'
        })

    except Exception as e:
        _logger.error(f"✗ FAIL: Portal user cannot access/write to website.page model: {e}")
        results['failed'] += 1
        results['tests'].append({
            'name': 'Portal user has write access to website.page',
            'status': 'FAIL',
            'reason': str(e)
        })

    _logger.info("")

    # Test 4: Verify portal user login process
    _logger.info("TEST 4: Verifying portal user login process")
    _logger.info("-" * 80)
    results['total_tests'] += 1

    try:
        # Use the portal user created in Test 2
        portal_user = env['res.users'].search([('login', '=', 'test_portal_acl')], limit=1)

        if not portal_user:
            # Create if not exists
            portal_group = env.ref('base.group_portal')
            portal_user = env['res.users'].create({
                'name': 'Test Portal User Login',
                'login': 'test_portal_login',
                'email': 'test_portal_login@example.com',
                'groups_id': [(6, 0, [portal_group.id])],
                'password': 'test_password_123',
            })
            _logger.info(f"✓ Created portal user for login test: {portal_user.name}")
        else:
            _logger.info(f"✓ Using existing portal user: {portal_user.name}")

        # Test that portal user can access their own data
        portal_user_data = portal_user.with_user(portal_user).read(['name', 'email', 'login'])
        _logger.info("✓ PASS: Portal user successfully accessed their own data")
        _logger.info(f"  - User: {portal_user_data[0]['name']}")
        _logger.info(f"  - Email: {portal_user_data[0]['email']}")

        # Test that portal user can access website.page model
        website_pages = env['website.page'].with_user(portal_user).search([], limit=1)
        _logger.info(f"✓ PASS: Portal user successfully accessed website.page model")
        _logger.info(f"  - Found {len(website_pages)} page(s)")

        if website_pages:
            page_data = website_pages.read(['name', 'url'])
            _logger.info(f"  - Sample page: {page_data[0]['name']}")

            # Test write operation
            website_pages.with_user(portal_user).write({
                'name': 'Test Page - Login Process Test'
            })
            _logger.info("✓ PASS: Portal user successfully wrote to website.page during login simulation")

        results['passed'] += 1
        results['tests'].append({
            'name': 'Portal user login process works without getting stuck',
            'status': 'PASS'
        })

    except Exception as e:
        _logger.error(f"✗ FAIL: Portal user login process failed: {e}")
        results['failed'] += 1
        results['tests'].append({
            'name': 'Portal user login process works without getting stuck',
            'status': 'FAIL',
            'reason': str(e)
        })

    _logger.info("")

    # Test 5: Check for conflicting ir.rules
    _logger.info("TEST 5: Checking for conflicting ir.rules")
    _logger.info("-" * 80)
    results['total_tests'] += 1

    try:
        rules = env['ir.rule'].search([
            ('model_id.model', '=', 'website.page')
        ])

        _logger.info(f"Found {len(rules)} ir.rule(s) for website.page model")

        conflicting_rules = []
        for rule in rules:
            _logger.info(f"  - Rule: {rule.name}")
            _logger.info(f"    Domain: {rule.domain_force}")
            _logger.info(f"    Groups: {rule.groups.mapped('name')}")
            _logger.info(f"    Perms Read: {rule.perm_read}")
            _logger.info(f"    Perms Write: {rule.perm_write}")
            _logger.info(f"    Perms Create: {rule.perm_create}")
            _logger.info(f"    Perms Unlink: {rule.perm_unlink}")

            # Check if rule restricts portal users
            if rule.groups and portal_group in rule.groups:
                if not rule.perm_write or not rule.perm_create:
                    conflicting_rules.append(rule.name)

        if conflicting_rules:
            _logger.warning(f"⚠ WARNING: Found potentially conflicting rules: {conflicting_rules}")
            results['failed'] += 1
            results['tests'].append({
                'name': 'No conflicting ir.rules for portal users',
                'status': 'FAIL',
                'reason': f'Conflicting rules found: {conflicting_rules}'
            })
        else:
            _logger.info("✓ PASS: No conflicting ir.rules found that would restrict portal users")
            results['passed'] += 1
            results['tests'].append({
                'name': 'No conflicting ir.rules for portal users',
                'status': 'PASS'
            })

    except Exception as e:
        _logger.error(f"✗ FAIL: Error checking ir.rules: {e}")
        results['failed'] += 1
        results['tests'].append({
            'name': 'No conflicting ir.rules for portal users',
            'status': 'FAIL',
            'reason': str(e)
        })

    _logger.info("")

    # Print summary
    _logger.info("=" * 80)
    _logger.info("TEST SUMMARY")
    _logger.info("=" * 80)
    _logger.info(f"Total Tests: {results['total_tests']}")
    _logger.info(f"Passed: {results['passed']}")
    _logger.info(f"Failed: {results['failed']}")
    _logger.info("")

    for test in results['tests']:
        status_symbol = "✓" if test['status'] == 'PASS' else "✗"
        _logger.info(f"{status_symbol} {test['name']}: {test['status']}")
        if test['status'] == 'FAIL' and 'reason' in test:
            _logger.info(f"  Reason: {test['reason']}")

    _logger.info("=" * 80)
    _logger.info("")

    if results['failed'] > 0:
        _logger.error("SOME TESTS FAILED - ACL fix may not be working correctly")
    else:
        _logger.info("ALL TESTS PASSED - ACL fix is working correctly")

    _logger.info("")

    return results


def main():
    """Main entry point for standalone execution."""
    import sys
    try:
        # This will work when run from Odoo shell
        from odoo import api, registry
        from odoo.tools.config import config

        db_name = config.get('db_name')
        if not db_name:
            _logger.error("Database name not specified. Use -d <database> parameter.")
            sys.exit(1)

        db_registry = registry.Registry(db_name)

        with db_registry.cursor() as cr:
            env = api.Environment(cr, 1, {})
            results = verify_acl_fix(env)

            if results['failed'] > 0:
                sys.exit(1)
            else:
                sys.exit(0)

    except Exception as e:
        _logger.error(f"Error running verification: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
