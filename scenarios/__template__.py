from scenarios import Scenario


class Import(Scenario):
    """
        Template class for creating new scenarios.
    """
    name = "Name"
    enabled = False
    weight = -1

    def create_network(self, controller=None):
        super(Import, self).create_network(controller)

    def run_network(self):
        super(Import, self).run_network()

    def generate_task(self, doc):
        Scenario.generate_task(self, doc)
        doc.add_paragraph("Template")

    def generate_questions(self):
        self.questions += [("Template Question", "Template Answer")]


if __name__ == "__main__":
    # Run network
    Import(developer=True, seed="debug").run()
