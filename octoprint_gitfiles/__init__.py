# coding=utf-8
from __future__ import absolute_import
from subprocess import check_output
from subprocess import call
from octoprint.settings import settings, valid_boolean_trues
import octoprint.plugin
import os

class GitfilesPlugin(octoprint.plugin.SettingsPlugin,
                     octoprint.plugin.AssetPlugin,
										 octoprint.plugin.SimpleApiPlugin,
                     octoprint.plugin.TemplatePlugin):

	def get_settings_defaults(self):
		return dict(url="https://github.com/YourUserID/YourRepository.git", path="gitfiles")

	def get_template_vars(self):
		return dict(url=self._settings.get(["url"]), path=self._settings.get(["path"]))

	def get_template_configs(self):
		return [dict(type="settings", custom_bindings=False)]

	def get_assets(self):
		return dict(
			js=["js/gitfiles.js"],
			css=["css/gitfiles.css"],
			less=["less/gitfiles.less"]
		)

	def get_api_commands(self):
		return dict(
			git=["arg1"]
		)

	def on_api_command(self, command, data):
		import flask
		if command == "git":
			if self._settings.get(["url"]) == "https://github.com/YourUserID/YourRepository.git":
				self._logger.info("Problem with setup. Please visit Settings -> GitFiles and adjust the URL")
				return

			uploads = self._settings.global_get_basefolder("uploads")
			path =    self._settings.get(["path"])
			url =     self._settings.get(["url"])
			verb =    "{arg1}".format(**data)
			
			if path == "" or path == "uploads":
				gitfilesFolder = uploads
			else:
				gitfilesFolder = uploads + "/" + path
			self._logger.info("Path: `{}`".format(gitfilesFolder))
			# In the indicated path, issue a `git remote get-url origin` to determine whether
			# or not it's been initialized before
			try:
				self._logger.info("Testing the indicated `{}` folder...".format(gitfilesFolder))
				output =  call(["git", "remote", "get-url", "origin"], cwd=gitfilesFolder)
				if output > 0:
					self.init(output, gitfilesFolder, url)
			except OSError as e:
				self._logger.info("Indicated folder is not initialized yet, throwing error")
				output = "N/A"
				self.init(output, gitfilesFolder, url)

			# This one runs regardless of whether or not it's been previously initialized
			try:
				self._logger.info("-- git {} origin master ---------------------------------------------------".format(verb))
				output =  call(["git", verb, "origin", "master"], cwd=gitfilesFolder)
				self._logger.info("git returned: " + str(output))
				self._logger.info("-- (end of git {}) --------------------------------------------------------".format(verb))
			except OSError as e:
				self._logger.info("`git {}` failed".format(verb))

	def init(self, output, gitfilesFolder, url):
		self._logger.info("Path is not initialized already, returned error: `{}`".format(output))
		# TODO: Test to see if the output is the correct remote
		if not os.path.isdir(gitfilesFolder):
			try:
				self._logger.info("Creating the new `{}` subfolder...".format(gitfilesFolder))
				os.mkdir(gitfilesFolder, 0o0755)
				self._logger.info("Created")
			except OSError as e:
				self._logger.info("Subfolder creation failed")
				return
		try:
			self._logger.info("Initializing...")
			output =  call(["git", "init"], cwd=gitfilesFolder)
			self._logger.info(output)
		except OSError as e:
			self._logger.info("`git init` failed")
			return
		try:
			self._logger.info("Setting up the remote origin for master...")
			output =  call(["git", "remote", "add", "origin", url], cwd=gitfilesFolder)
			self._logger.info(output)
		except OSError as e:
			self._logger.info("`git add remote origin` failed")
			return

	def get_update_information(self):
		return dict(
			gitfiles=dict(
				displayName="Gitfiles Plugin",
				displayVersion=self._plugin_version,
				type="github_release",
				user="OutsourcedGuru",
				repo="OctoPrint-GitFiles",
				current=self._plugin_version,
				pip="https://github.com/OutsourcedGuru/OctoPrint-GitFiles/archive/{target_version}.zip"
			)
		)

__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = GitfilesPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
