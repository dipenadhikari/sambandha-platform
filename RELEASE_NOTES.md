# v0.1 release notes

## Outcome

This release converts the Sambandha concept into a repository-ready, testable business workflow. It connects a public preliminary quotation to an authenticated staff follow-up process.

## Verification completed

- Dependency lock generated with Django 5.2.17 LTS
- Initial database migration generated and applied
- Eight automated tests passed
- Django system check passed
- Django production deployment check passed with production-like environment values
- Static assets collected successfully
- Smoke responses verified: public home `200`, quotation `200`, staff workspace redirects unauthenticated visitors to sign-in

## Product risks still open

- Pricing has not been verified by Sambandha management or suppliers.
- No real customer interview or staff usability test has been recorded.
- No production hosting, backup, monitoring, notification, or privacy process exists yet.
- No real customer data should be entered into a public portfolio deployment.

## Next decision

Run a staff walkthrough using ten synthetic inquiries. Record where staff still need WhatsApp, paper, or spreadsheets. That evidence should determine v0.2—not a generic feature wishlist.

