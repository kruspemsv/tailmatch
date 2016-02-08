# tailmatch
### Monitorador de logs

#### Descrição
tailmatch é um programa que busca as ocorrências de uma determinada expressão regular em um ou mais arquivos de forma contínua obedecendo um intervalo de tempo determinado no início de sua execução.

#### Uso
```
usage: ./tailmatch.py [-h] -a [ARQUIVOS [ARQUIVOS ...]] [-s SLEEP] -R REGEX
                      [-v VERBOSE]

optional arguments:
  -h, --help            show this help message and exit
  -a [ARQUIVOS [ARQUIVOS ...]], --arquivos [ARQUIVOS [ARQUIVOS ...]]
                        Arquivo(s) para monitorar.
  -s SLEEP, --sleep SLEEP
                        Intervalo do check. Default 60
  -R REGEX, --regex REGEX
                        Regex para ser buscada
  -v VERBOSE, --verbose VERBOSE
                        Lista verbose
```

#### Exemplos

```
[root@centos6 log]# echo "joao" >> teste.log
[root@centos6 log]# echo "guilherme" >> teste.log
[root@centos6 log]# echo "marcelo" >> teste.log
[root@centos6 log]# echo "bruna" >> teste.log
[root@centos6 log]# echo "ines" >> teste.log
[root@centos6 log]# echo "marmelo" >> teste.log
[root@centos6 log]# echo "martelo" >> teste.log

[root@centos6 log]# tailmatch.py -a teste.log -R "mar(c|m|t)elo" -s 10
1454949861 - Iniciando processo com sleep de 10.
1454949891 - 1 resultados para 'mar(c|m|t)elo' no arquivo teste.log.
1454949911 - 2 resultados para 'mar(c|m|t)elo' no arquivo teste.log.
```

Para monitorar diversos arquivos é possível se beneficiar da expansão de shell:

```
[root@centos6 log]# tailmatch.py -a $(find /var/log/ -maxdepth 1 -type f) -R "[\d]{1,3}$" -s 10
1454950203 - Iniciando processo com sleep de 10.
1454950224 - 1 resultados para '[\d]{1,3}$' no arquivo /var/log/yum.log.
1454950244 - 1 resultados para '[\d]{1,3}$' no arquivo /var/log/messages.
```

tailmatch é capaz de saber quando um arquivo foi truncado/removido e seguir normalmente seu monitoramento após restabelecido:

```
[root@centos6 log]# tailmatch.py -a teste.log -R "mar(c|m|t)elo" -s 10
1454950297 - Iniciando processo com sleep de 10.

[root@centos6 log]# echo "bruna" >> teste.log
[root@centos6 log]# echo "marcelo" >> teste.log

[root@centos6 log]# tailmatch.py -a teste.log -R "mar(c|m|t)elo" -s 10
1454950297 - Iniciando processo com sleep de 10.
1454950317 - 1 resultados para 'mar(c|m|t)elo' no arquivo teste.log.

[root@centos6 log]# >teste.log
[root@centos6 log]# echo "ines" >> teste.log
[root@centos6 log]# echo "marmelo" >> teste.log

[root@centos6 log]# tailmatch.py -a teste.log -R "mar(c|m|t)elo" -s 10
1454950297 - Iniciando processo com sleep de 10.
1454950317 - 1 resultados para 'mar(c|m|t)elo' no arquivo teste.log.
1454950357 - 1 resultados para 'mar(c|m|t)elo' no arquivo teste.log.

[root@centos6 log]# tailmatch.py -a teste.log -R "mar(c|m|t)elo" -s 10
1454950297 - Iniciando processo com sleep de 10.
1454950317 - 1 resultados para 'mar(c|m|t)elo' no arquivo teste.log.
1454950357 - 1 resultados para 'mar(c|m|t)elo' no arquivo teste.log.

[root@centos6 log]# rm -f teste.log

CRITICAL: Arquivo teste.log. Erro: No such file or directory
CRITICAL: Arquivo teste.log. Erro: No such file or directory
CRITICAL: Arquivo teste.log. Erro: No such file or directory
CRITICAL: Arquivo teste.log. Erro: No such file or directory

[root@centos6 log]# echo "martelo" >> teste.log

[root@centos6 log]# tailmatch.py -a teste.log -R "mar(c|m|t)elo" -s 10
1454950297 - Iniciando processo com sleep de 10.
[...]
1454950487 - 1 resultados para 'mar(c|m|t)elo' no arquivo teste.log.
```

stdout e stderr são implementados normalmente no programa:

```
[root@centos6 log]# tailmatch.py -a teste.log -R "mar(c|m|t)elo" -s 10 2> erro.log
1454950589 - Iniciando processo com sleep de 10.
1454950599 - 1 resultados para 'mar(c|m|t)elo' no arquivo teste.log.

[root@centos6 log]# echo "marcelo" >> teste.log
[root@centos6 log]# rm -f teste.log

[root@centos6 log]# cat erro.log
CRITICAL: Arquivo teste.log. Erro: No such file or directory
CRITICAL: Arquivo teste.log. Erro: No such file or directory
```

#### Sobre
Dúvidas, sugestões, melhorias ou bugs: marcelo.varge@gmail.com
