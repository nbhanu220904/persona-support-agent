# SAML single sign-on

Workspace owners can configure SAML 2.0 from Settings > Security > Single sign-on. Lumina requires the identity provider metadata URL or XML, an email NameID, and signed assertions. Copy Lumina's ACS URL and entity ID exactly into the identity provider.

For login loops, confirm the email NameID matches the Lumina account, system clocks differ by less than five minutes, and the assertion audience equals the Lumina entity ID. Keep one break-glass owner account outside SSO until configuration is tested.

