# Modmail Plugins

This repository hosts several custom plugins for Modmail.

## Modwhat?

Modmail is a bot that provides a shared inbox for server staff to communicate with their users.

The most popular variation is [the one by kyb3r][kyb3r-modmail]. These plugins extend the functionality of it, by providing cogs that can be sideloaded.

## Plugins

Each plugin has a specific purpose, listed in further detail below. You can install one of them by using the following command.

```sh
?plugins add robinmahieu/modmail-plugins/plugin-name@stardust
```

Make sure to change the `plugin-name` dummy variable to a valid plugin name, like `autorole`, `embedder`, `purger`, `role-assignment` or `supporters`. Keep in mind that the default branch of this repository has an unconventional name and should be stated explicitly . If not, an `InvalidPluginError` is raised when trying to install one of these plugins.

### Autorole

This plugin is intended to assign roles to members when they join the server.

### Embedder

This plugin is intended to easily embed text.

### Purger

This plugin is intended to delete multiple messages at once.

### Role Assignment

This plugin is intended to assign roles by clicking reactions.

Please note that this plugin does not provide the usual reaction roles.

### Supporters

This plugin is intended to view which members are part of the support team.

## Contributing

This project is licensed under the terms of the [MIT][mit-license] license.

[kyb3r-modmail]: <https://github.com/kyb3r/modmail>
[mit-license]: <https://github.com/robinmahieu/modmail-plugins/blob/stardust/LICENSE>
