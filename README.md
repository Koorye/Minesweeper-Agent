# Minesweeper Agent

A LLM-based Minesweeper Agent. [Paper](https://github.com/Koorye/Minesweeper-Agent/blob/main/minesweeper_agent.pdf).

**This project is for educational purposes only.**

## How to use

1. Install requirements:

```bash
pip install -r requirements.txt
```

2. Starting the api Service with Docker (Recommended):

```bash
docker run -it -d --init --name glm-free-api -p 8000:8000 -e TZ=Asia/Shanghai vinlic/glm-free-api:latest
```

3. Getting the token from the LLM website [ChatGLM](https://chatglm.cn/):

![](https://github.com/LLM-Red-Team/glm-free-api/raw/master/doc/example-0.png)

And then replace the token in `agent.py`.

4. Running `agent.py`:

```bash
python agent.py
```

## Custom LLM

You can use different LLM via using different Docker images:

- ChatGLM: `docker run -it -d --init --name glm-free-api -p 8000:8000 -e TZ=Asia/Shanghai vinlic/glm-free-api:latest`
- Spark: `docker run -it -d --init --name spark-free-api -p 8000:8000 -e TZ=Asia/Shanghai vinlic/spark-free-api:latest`
- Qwen: `docker run -it -d --init --name qwen-free-api -p 8000:8000 -e TZ=Asia/Shanghai vinlic/qwen-free-api:latest`

## Thanks

Thanks to the [LLM-Red-Team](https://github.com/LLM-Red-Team) for providing the LLM API service.

## Citation

```bibtex
@misc{minesweeper-agent,
  author = {Shihan Wu},
  title = {Minesweeper Agent: Exploring the Reasoning Ability of Large Language Models},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/Koorye/Minesweeper-Agent}},
}
