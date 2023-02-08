from prefect.infrastructure.docker import DockerContainer

docker_block = DockerContainer(
    image="try/prefect:zoomcamp",
    image_pull_policy="ALWAYS",
    auto_remove=True
    
)

docker_block.save("zoomcamp", overwrite=True)


