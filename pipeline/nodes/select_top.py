from pipeline.core.node import Node


class SelectTopNode(Node):

    name = 'select_top'

    def __init__(self, top_n=10):
        self.top_n = top_n

    def run(self, ctx):
        images = ctx.get('selected_images')
        scores = ctx.get('scores')

        scored = [scores[f] for f in images]
        scored.sort(key=lambda x: x['total_score'], reverse=True)
        ctx.set("selected", scored[:self.top_n])
        print(scored)
        print("Top selected:")
