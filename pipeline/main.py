import uvicorn

from backend.pipeline_runner import build_dag
from pipeline.core.executor import DAGExecutor
from pipeline.core.context import WorkflowContext


# def main():
#     ctx = WorkflowContext()
#     dag = build_dag("C:\\Users\\looge\\Desktop\\images\\1030")
#     executor = DAGExecutor(dag, max_workers=4)
#     executor.run(ctx)


# if __name__ == "__main__":
#     main()


if __name__ == "__main__":
    uvicorn.run("backend.server:app", host="localhost", port=8000, reload=True)
