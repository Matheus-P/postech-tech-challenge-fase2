# data/

**Nada aqui é versionado.** O `.gitignore` bloqueia o conteúdo destas pastas de propósito:
datasets em Git incham o repositório e frequentemente violam a licença da fonte.

| Pasta | Conteúdo |
|---|---|
| `raw/` | arquivo original, exatamente como baixado da fonte — nunca editado |
| `processed/` | saída dos notebooks de pré-processamento (`.parquet` ou `.csv`) |

Documente abaixo como obter os dados brutos, para que qualquer pessoa consiga reproduzir o projeto.

## Como obter

1. Baixe em: https://drive.google.com/file/d/1z4yEyiCE_CGCWbvAAZQZSz-5-E5T5eYd/view?usp=sharing
2. Salve como: `data/raw/application_record.csv`; `data/raw/credit_record.csv`
3. Checksum: 
`shasum -a 256 data/raw/application_record.csv  4833f502d02ad94295de3ffe74f665e726a4b04342d2e94f8cec41dce951925b`
`shasum -a 256 data/raw/credit_record.csv   ba0006a4734f74422d68b0a7132ad591850be0a6affb535eb1042d207fe4b27e`
