# bob

Inspirado pelo [nob.h](https://github.com/tsoding/nob.h) do tsoding, uma ferramenta que builda o projeto sozinho.

em vez de um `requirements.txt` que você precisa rodar manualmente, o `bob.py` detecta as dependências do seu projeto, instala o que falta e executa tudo com um único comando.

## como funciona

bob varre os `.py` do seu projeto usando `ast`, coleta os imports, filtra o que já é stdlib e instala só o que falta. Se o ambiente for gerenciado (Debian/Ubuntu), ele tenta `--break-system-packages` ou cria um venv automaticamente. 

pode ser perigoso? pode, mas as distros que eu uso não usam python no sistema, então por enquanto não me importo.

```
python3 bob.py
```

pronto.

## uso

```bash
python3 bob.py          # instala deps e roda main.py
python3 bob.py -c       # limpa a tela após instalar
python3 bob.py -e       # gera executável via pyinstaller (dist/main)
python3 bob.py -c -e    # os dois
```

## flags

| flag | descrição |
|------|-----------|
| `-c` | limpa a tela após a instalação das deps |
| `-e` | compila o projeto em executável único com pyinstaller |

tudo que bob faz fica registrado em `bob_log.txt`.

## estrutura esperada

```
meu-projeto/
├── bob.py      # o builder
├── main.py     # entry point do seu projeto
└── bob_log.txt # gerado automaticamente
```

## ordem de tentativa de instalação

1. `pip install` normal
2. `pip install --break-system-packages` (Debian/Ubuntu)
3. cria `.bob-venv/` e se relança dentro dele

## inspiração

[tsoding/nob.h](https://github.com/tsoding/nob.h) é a mesma ideia, mas em C. 
