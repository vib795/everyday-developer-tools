from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task
    def random_string_generator(self):
        # Simulate a POST request to the random_string_generator endpoint
        self.client.post("/string-tools/random-string-generator", data={"length": "1111111111"})

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
