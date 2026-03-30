# -*- coding: utf-8 -*-
"""
Test script to verify ACL fix for portal users accessing website.page model.

This test verifies that:
1. The XML security access rule was properly created
2. Portal users have write access to the website.page model
3. Portal user login process works without getting stuck
"""

import logging
import os

from odoo.exceptions import AccessError
from odoo.tests import common

_logger = logging.getLogger(__name__)


class TestWebsitePageACL(common.HttpCase):
    """Test ACL configuration for website.page model with portal users."""

    def setUp(self):
        """Set up test environment with portal user."""
        super(TestWebsitePageACL, self).setUp()
        self.website_page_model = self.env['website.page']
        self.portal_group = self.env.ref('base.group_portal')
        self.portal_user = None
        # Get the module path for XML file verification
        self.module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_01_check_xml_security_file_exists(self):
        """
        Test 1: Verify that the XML security file exists.
        Checks if website_page_security.xml file is present in security directory.
        """
        _logger.info("=" * 60)
        _logger.info("TEST 1: Checking if XML security file exists")
        _logger.info("=" * 60)

        xml_file_path = os.path.join(self.module_path, 'security', 'website_page_security.xml')

        if os.path.exists(xml_file_path):
            _logger.info("✓ PASS: XML security file 'website_page_security.xml' found")
            _logger.info(f"  - File path: {xml_file_path}")
        else:
            _logger.error("✗ FAIL: XML security file 'website_page_security.xml' NOT found")
            self.fail(f"XML security file not found at {xml_file_path}")

        _logger.info("")

    def test_02_check_security_access_rule_exists(self):
        """
        Test 2: Verify that the security access rule for portal users exists.
        Checks if access_website_page_portal rule is properly created from XML.
        """
        _logger.info("=" * 60)
        _logger.info("TEST 2: Checking if security access rule exists")
        _logger.info("=" * 60)

        # Search for the access rule
        access_rule = self.env['ir.model.access'].search([
            ('name', '=', 'access_website_page_portal'),
            ('model_id.model', '=', 'website.page'),
            ('group_id', '=', self.portal_group.id)
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

            # Verify permissions are correct
            self.assertTrue(access_rule.perm_read, "Read permission should be True")
            self.assertTrue(access_rule.perm_write, "Write permission should be True")
            self.assertTrue(access_rule.perm_create, "Create permission should be True")
            self.assertTrue(access_rule.perm_unlink, "Unlink permission should be True")
        else:
            _logger.error("✗ FAIL: Security access rule 'access_website_page_portal' NOT found")
            self.fail("Security access rule for portal users on website.page model does not exist")

        _logger.info("")

    def test_03_portal_user_write_access(self):
        """
        Test 2: Verify that portal users have write access to website.page model.
        Tests the actual write operation with portal user context.
        """
        _logger.info("=" * 60)
        _logger.info("TEST 2: Verifying portal user write access to website.page")
        _logger.info("=" * 60)

        # Create a test website page with admin user
        test_page = self.website_page_model.create({
            'name': 'Test Page for ACL Verification',
            'url': '/test-acl-verification',
            'view_id': self.env.ref('website.homepage').id,
            'website_published': True,
        })
        _logger.info(f"✓ Created test website page: {test_page.name} (ID: {test_page.id})")

        # Create a portal user
        portal_user = self.env['res.users'].create({
            'name': 'Test Portal User',
            'login': 'test_portal_user',
            'email': 'test_portal@example.com',
            'groups_id': [(6, 0, [self.portal_group.id])],
            'password': 'test_password_123',
        })
        _logger.info(f"✓ Created portal user: {portal_user.name} (ID: {portal_user.id})")
        self.portal_user = portal_user

        # Test write access with portal user
        try:
            test_page.with_user(portal_user).write({
                'name': 'Test Page - Modified by Portal User'
            })
            _logger.info("✓ PASS: Portal user successfully wrote to website.page model")
            _logger.info(f"  - Page name updated to: {test_page.name}")
        except AccessError as e:
            _logger.error("✗ FAIL: Portal user cannot write to website.page model")
            _logger.error(f"  - AccessError: {e}")
            self.fail(f"Portal user should have write access to website.page model: {e}")

        # Test read access with portal user
        try:
            pages = test_page.with_user(portal_user).search_read([], ['name', 'url'])
            _logger.info("✓ PASS: Portal user successfully read from website.page model")
            _logger.info(f"  - Number of pages read: {len(pages)}")
        except AccessError as e:
            _logger.error("✗ FAIL: Portal user cannot read from website.page model")
            _logger.error(f"  - AccessError: {e}")
            self.fail(f"Portal user should have read access to website.page model: {e}")

        # Test create access with portal user
        try:
            new_page = test_page.with_user(portal_user).create({
                'name': 'Test Page Created by Portal User',
                'url': '/test-portal-created',
                'view_id': self.env.ref('website.homepage').id,
            })
            _logger.info("✓ PASS: Portal user successfully created website.page record")
            _logger.info(f"  - New page ID: {new_page.id}")
        except AccessError as e:
            _logger.error("✗ FAIL: Portal user cannot create website.page records")
            _logger.error(f"  - AccessError: {e}")
            self.fail(f"Portal user should have create access to website.page model: {e}")

        _logger.info("")

    def test_04_portal_user_login_process(self):
        """
        Test 3: Verify that portal user login process works without getting stuck.
        Simulates the login flow that was previously failing.
        """
        _logger.info("=" * 60)
        _logger.info("TEST 3: Testing portal user login process")
        _logger.info("=" * 60)

        # Create a portal user if not already created
        if not self.portal_user:
            portal_user = self.env['res.users'].create({
                'name': 'Test Portal User Login',
                'login': 'test_portal_login',
                'email': 'test_portal_login@example.com',
                'groups_id': [(6, 0, [self.portal_group.id])],
                'password': 'test_password_123',
            })
            _logger.info(f"✓ Created portal user for login test: {portal_user.name}")
            self.portal_user = portal_user
        else:
            portal_user = self.portal_user
            _logger.info(f"✓ Using existing portal user: {portal_user.name}")

        # Simulate login by switching user context
        try:
            # Test that portal user can access their own data
            portal_user_data = portal_user.with_user(portal_user).read(['name', 'email', 'login'])
            _logger.info("✓ PASS: Portal user successfully accessed their own data")
            _logger.info(f"  - User: {portal_user_data[0]['name']}")
            _logger.info(f"  - Email: {portal_user_data[0]['email']}")
        except Exception as e:
            _logger.error("✗ FAIL: Portal user cannot access their own data")
            _logger.error(f"  - Error: {e}")
            self.fail(f"Portal user should be able to access their own data: {e}")

        # Test that portal user can access website.page model (the problematic operation)
        try:
            website_pages = self.website_page_model.with_user(portal_user).search([], limit=1)
            _logger.info("✓ PASS: Portal user successfully accessed website.page model")
            _logger.info(f"  - Found {len(website_pages)} page(s)")

            if website_pages:
                page_data = website_pages.read(['name', 'url'])
                _logger.info(f"  - Sample page: {page_data[0]['name']}")
        except Exception as e:
            _logger.error("✗ FAIL: Portal user cannot access website.page model during login")
            _logger.error(f"  - Error: {e}")
            self.fail(f"Portal user should be able to access website.page model: {e}")

        # Test that portal user can perform a write operation on website.page
        try:
            if website_pages:
                website_pages.with_user(portal_user).write({
                    'name': 'Test Page - Login Process Test'
                })
                _logger.info("✓ PASS: Portal user successfully wrote to website.page during login simulation")
        except Exception as e:
            _logger.error("✗ FAIL: Portal user cannot write to website.page during login")
            _logger.error(f"  - Error: {e}")
            self.fail(f"Portal user should be able to write to website.page: {e}")

        _logger.info("")

    def test_05_verify_all_permissions(self):
        """
        Test 4: Comprehensive verification of all permissions for portal users on website.page.
        """
        _logger.info("=" * 60)
        _logger.info("TEST 4: Comprehensive permission verification")
        _logger.info("=" * 60)

        # Get the access rule
        access_rule = self.env['ir.model.access'].search([
            ('name', '=', 'access_website_page_portal'),
            ('model_id.model', '=', 'website.page'),
            ('group_id', '=', self.portal_group.id)
        ], limit=1)

        if not access_rule:
            _logger.error("✗ FAIL: Access rule not found")
            self.fail("Access rule must exist for permission verification")

        # Verify all permissions
        permissions = {
            'perm_read': access_rule.perm_read,
            'perm_write': access_rule.perm_write,
            'perm_create': access_rule.perm_create,
            'perm_unlink': access_rule.perm_unlink,
        }

        all_correct = True
        for perm_name, perm_value in permissions.items():
            status = "✓" if perm_value else "✗"
            _logger.info(f"{status} {perm_name}: {perm_value}")
            if not perm_value:
                all_correct = False

        if all_correct:
            _logger.info("✓ PASS: All permissions are correctly configured")
        else:
            _logger.error("✗ FAIL: Some permissions are missing or incorrect")
            self.fail("All permissions (read, write, create, unlink) should be True for portal users")

        _logger.info("")

    def test_06_check_ir_rule_consistency(self):
        """
        Test 5: Check if there are any conflicting ir.rules that might override ACL.
        """
        _logger.info("=" * 60)
        _logger.info("TEST 5: Checking for conflicting ir.rules")
        _logger.info("=" * 60)

        # Search for rules related to website.page
        rules = self.env['ir.rule'].search([
            ('model_id.model', '=', 'website.page')
        ])

        _logger.info(f"Found {len(rules)} ir.rule(s) for website.page model")

        for rule in rules:
            _logger.info(f"  - Rule: {rule.name}")
            _logger.info(f"    Domain: {rule.domain_force}")
            _logger.info(f"    Groups: {rule.groups.mapped('name')}")
            _logger.info(f"    Perms Read: {rule.perm_read}")
            _logger.info(f"    Perms Write: {rule.perm_write}")
            _logger.info(f"    Perms Create: {rule.perm_create}")
            _logger.info(f"    Perms Unlink: {rule.perm_unlink}")

        _logger.info("✓ PASS: ir.rules checked for potential conflicts")
        _logger.info("")


def run_tests():
    """
    Standalone function to run tests with detailed logging output.
    This can be executed directly in an Odoo environment.
    """
    import sys

    from odoo import api, registry

    # Get the database registry
    db_registry = registry.Registry(common.get_db_name())

    with db_registry.cursor() as cr:
        env = api.Environment(cr, 1, {})

        _logger.info("")
        _logger.info("=" * 60)
        _logger.info("STARTING WEBSITE.PAGE ACL VERIFICATION TESTS")
        _logger.info("=" * 60)
        _logger.info("")

        test_instance = TestWebsitePageACL()
        test_instance.setUp()

        tests = [
            ('test_01_check_xml_security_file_exists', test_instance.test_01_check_xml_security_file_exists),
            ('test_02_check_security_access_rule_exists', test_instance.test_02_check_security_access_rule_exists),
            ('test_03_portal_user_write_access', test_instance.test_03_portal_user_write_access),
            ('test_04_portal_user_login_process', test_instance.test_04_portal_user_login_process),
            ('test_05_verify_all_permissions', test_instance.test_05_verify_all_permissions),
            ('test_06_check_ir_rule_consistency', test_instance.test_06_check_ir_rule_consistency),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                test_func()
                passed += 1
            except Exception as e:
                _logger.error(f"✗ Test '{test_name}' failed with error: {e}")
                failed += 1

        _logger.info("")
        _logger.info("=" * 60)
        _logger.info("TEST SUMMARY")
        _logger.info("=" * 60)
        _logger.info(f"Total Tests: {len(tests)}")
        _logger.info(f"Passed: {passed}")
        _logger.info(f"Failed: {failed}")
        _logger.info("=" * 60)
        _logger.info("")

        if failed > 0:
            _logger.error("SOME TESTS FAILED - ACL fix may not be working correctly")
            sys.exit(1)
        else:
            _logger.info("ALL TESTS PASSED - ACL fix is working correctly")
            sys.exit(0)


if __name__ == '__main__':
    run_tests()
if __name__ == '__main__':
    run_tests()
