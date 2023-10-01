# Modmail Plugins

This repository hosts several custom plugins for Modmail.

## Mod-what?

Modmail is a bot for [Discord][discord] that provides a shared inbox for server staff and regular members to communicate with each other.

These plugins extend the functionality of the [https://github.com/modmail-dev/Modmail][modmail] adaptation, by providing additional commands.

Currently, all of the plugins support Modmail version 4.0.0 and higher.

## Plugins

Each plugin has a distinct purpose, as described below. After installing one of the plugins, a dedicated page in the help menu provides more information about its commands.

You can install a plugin by using the following command.

```sh
?plugins add robinmahieu/modmail-plugins/plugin-name@stardust
```

Make sure to replace the `plugin-name` dummy variable with a valid plugin name, like `autorole`, `embedder`, `purger`, `role-assignment` or `supporters`. Keep in mind that the default branch of this repository has an unconventional name and should be stated explicitly. If not, an `InvalidPluginError` is raised when trying to install one of these plugins.

### Autorole

This plugin is intended to assign roles to members when they join the server.

### Embedder

This plugin is intended to easily embed text.

### Purger

This plugin is intended to delete multiple messages at once.

### Role Assignment

This plugin is intended to assign roles by clicking reactions.

Please note that this plugin does not provide the usual reaction roles. Instead, it allows server staff to assign roles to regular members when they open a thread. This could be useful when roles are only supposed to be assigned after explicit approval.

### Supporters

This plugin is intended to view which members are part of the support team.

## Contributing

This project is licensed under the terms of the [MIT][mit-license] license.

[discord]: <https://discord.com/>
[mit-license]: <https://github.com/robinmahieu/modmail-plugins/blob/stardust/LICENSE>
[modmail]: <https://github.com/modmail-dev/Modmail>
