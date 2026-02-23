---
name: letterly-update-subscription
description: Automates the process of starting a new 7-day free trial on Letterly and then immediately canceling the subscription (to prevent automatic charges after 7 days). This skill handles the navigation from Letterly to Stripe Checkout and then back to the Stripe Billing Portal for cancellation. Use when the user asks to "start a new trial", "update my subscription", or "reset my trial on letterly".
---

# Letterly Update Subscription

This skill automates the management of your Letterly subscription to leverage the 7-day free trial safely.

## Workflow Summary

1.  **Trial Start:**
    *   Navigates to `web.letterly.app`.
    *   Identifies the "Start 7-day trial" pop-up.
    *   Redirects to **Stripe Checkout** and attempts to click the "Start trial" confirmation.
2.  **Immediate Cancellation:**
    *   Navigates back to Letterly **Settings**.
    *   Finds the "Manage Subscription" or "Billing" link.
    *   Redirects to **Stripe Billing Portal** and attempts to click "Cancel plan" to prevent future charges.

## Usage

To trigger the automation, simply tell the model:
"Start a new 7-day trial on Letterly" or "Reset my trial on Letterly".

### Manual Execution

If you need to run it manually:

```bash
# Ensure you are in the skills directory
cd ai-agents-config/skills/
.venv/bin/python letterly-update-subscription/scripts/subscription_manager.py
```

## Requirements

*   **Persistent Login:** The script uses a persistent browser profile. You must have logged in to Letterly once through this agent for the session to be active.
*   **Stripe Account:** Your payment details should ideally be saved or pre-filled in Stripe for the automation to be fully seamless. If not, the script will wait for your manual interaction.
