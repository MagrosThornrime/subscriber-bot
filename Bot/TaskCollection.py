import discord as dc


class TaskCollection:
    def __init__(self, guild: dc.Guild):
        self.guild = guild
        self.tasks = []

    def create_task(self):
        # 1. create and send the modal:
        #   - name of the plugin
        #   - tag
        #   - (optional) name of the channel
        #   - period (minutes, days, months)
        #   - when to run it the first time
        #   - how many times to run it (Task object will have a counter)
        # 2. after getting the answer, check it, assign attributes and send another modal (if needed)
        # for the plugin. Repeat until the plugin says it's enough
        # 3. register the task to the list
        # 4. log the tasks
        pass

    def delete_task(self):
        # 1. create and send the modal - using command's arguments,
        # choose between using a filter or choosing an individual task,
        # then send specific modal
        # 2. select chosen tasks and stop, then delete them
        # 3. log the tasks
        pass

    def edit_task(self):
        # 1. create and send the modal - choose an individual task
        # 2. choose using arguments:
        #   - update common task's data (like tag, channel, period)
        #   - ask if the user wants to edit plugin's data
        # 3. create the new version of the task
        # 4. (optional) using modal, update common data
        # 5. (optional) prepare the task using the plugin (with using modals)
        # 6. delete the old version, start the new one
        pass

    def list_tasks(self):
        # 1. choose between using a filter or showing all the tasks
        # 2. (optional) choose the filter (using a modal)
        # 3. show all tasks
        pass

    def run_task(self):
        # 1. choose between using a filter or showing all the tasks
        # 2. (optional) choose the filter (using a modal)
        # 3. run all tasks
        # (running means forcing the tasks to generate and send their outputs)
        pass