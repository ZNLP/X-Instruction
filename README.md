<p align="center">
  <img src="assets/logo.jpg" alt="X-Instruction" width="200"/>
</p>

<h1 align="center">
  X-Instruction💥
</h1>

Official code and data for ACL-2024 paper "X-Instruction: Aligning Language Model in Low-resource Languages with Self-curated Cross-lingual Instructions"

## 📢 News

## 📝 Case Study

## 📚 Dataset
### X-Instruction Preparation
<p float="left">
    <img src="assets/method.png", width="100%">
</p>

- **X-Instruction Generation:** Language models learn to generate cross-lingual instructions for multilingual texts using seed data.
- **X-Instruction Refinement:** Language models iteratively label and refine cross-lingual instruction samples.
- **X-Instruction Diversification:** The final instruction data are sampled from different clusters of embedding from the English instruction to increase the diversity.

### Statistic of X-Instruction

| Language        | Instruction Length  | Output Length        |  Samples |
| --------------- | ------------------- | -------------------- | -------- |
| Finnish (fi)    | 100.7 ± 81.1        | 1026.9 ± 552.8       | $32k$    |
| Indonesian (id) | 101.0 ± 86.0        | 1008.9 ± 542.1       | $32k$    |
| Thai (th)       | 102.4 ± 85.0        | 987.5 ± 545.0        | $32k$    |
| Turkish (tr)    | 103.7 ± 87.5        | 1057.9 ± 534.1       | $32k$    |
| Vietnamese (vi) | 101.0 ± 86.0        | 1120.4 ± 561.1       | $32k$    |
| Bengali (bn)    | 111.9 ± 87.2        | 1243.4 ± 518.7       | $32k$    |
| Hindi (hi)      | 96.6 ± 79.9         | 1284.9 ± 506.2       | $32k$    |
| Swahili (sw)    | 100.0 ± 85.3        | 1210.6 ± 524.0       | $32k$    |
| Tamil (ta)      | 99.0 ± 84.8         | 1259.0 ± 497.8       | $32k$    |
| Urdu (ur)       | 107.6 ± 87.4        | 1246.9 ± 508.8       | $32k$    |

### 🙋 How to get it
📎 X-Instruction [Dataset](https://huggingface.co/James-WYang/X-Instruction)

📎 X-Instruction Model: [7B](https://huggingface.co/James-WYang/X-Instruction) [13B](https://huggingface.co/James-WYang/X-Instruction)


## 🛎 Getting Started
### 📌 Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

### 📌 Model Inference
   ```bash
   bash ./scripts/inference.sh
   ```

### 📌 Automatic Evaluation
   ```bash
   bash ./scripts/evaluation.sh
   ```

## License

## Acknowledgement





