# Changelog

## [Unreleased] - 2024

### Changed - No Authentication Mode

#### Backend Changes
- **Removed authentication requirement** from all API endpoints
- Updated `backend/app/api/routes/leads.py`:
  - Removed `current_user: User = Depends(get_current_active_user)` from all endpoints
  - All 7 endpoints now work without authentication

- Updated `backend/app/api/routes/campaigns.py`:
  - Removed authentication dependency from all 8 endpoints
  - Set `created_by=None` instead of `current_user.id`

- Updated `backend/app/api/routes/content.py`:
  - Removed authentication from all 10 endpoints
  - Set `created_by=None` and `approved_by=None`

#### Frontend Changes
- **Simplified App.jsx**:
  - Removed `AuthProvider` wrapper
  - Removed `ProtectedRoute` component
  - Removed login/register routes
  - All pages now directly accessible

- **Updated Navbar.jsx**:
  - Removed user display
  - Removed logout button
  - Simplified to show just branding

- **Updated api.js**:
  - Removed authentication token interceptor
  - Removed auto-redirect to login on 401

#### Documentation Updates
- Added `NO_AUTH_MODE.md` - Complete explanation of no-auth mode
- Updated `README.md` - Added no-login notice at top
- Updated `QUICKSTART.md` - Removed registration step
- Added `CHANGELOG.md` - This file

### Why This Change?

**Benefits:**
- ✅ Immediate use - no setup friction
- ✅ Perfect for solo entrepreneurs
- ✅ Great for testing and development
- ✅ Simpler deployment for single user
- ✅ Faster onboarding experience

**Trade-offs:**
- ⚠️ Not suitable for public multi-user deployments
- ⚠️ Requires network-level security for production
- ⚠️ No user-based access controls

### Security Recommendations

For local/development use: ✅ Perfectly safe
For production use:
- Use behind firewall/VPN
- Or re-enable authentication for multi-user access
- Consider adding HTTP basic auth at nginx level
- Use HTTPS always

### How to Re-enable Authentication

If you need authentication back:

1. Restore `Depends(get_current_active_user)` in backend routes
2. Restore user ID assignments (`created_by=current_user.id`)
3. Uncomment auth routes in frontend `App.jsx`
4. Restore `ProtectedRoute` wrapper
5. Restore token interceptor in `api.js`

All authentication code is still present, just not actively used.

---

## Previous Version (With Authentication)

The system previously included:
- JWT-based authentication
- User registration and login
- Protected routes
- User-specific data tracking
- Token-based API access

This functionality can be restored if needed for production multi-user deployments.
