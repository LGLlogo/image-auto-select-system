from core.node import Node


class SelectTopNode(Node):

    name = 'select_top'

    def __init__(self, top_n=10):
        self.top_n = top_n

    def run(self, ctx):
        scores = ctx.get('scores')
        scored = list(scores.items())
        scored.sort(key=lambda x: x[1].get('total_score'), reverse=True)
        ctx.set("selected", scored[:self.top_n])
        print("Top selected:")

        for img, scores in scored[:self.top_n]:
            print(scores.get('total_score'), img)
