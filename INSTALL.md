# Instalação do python-matter-aws-bridge

Esta ferramenta está composta por duas componentes, o **python-matter-aws-bridge**, que faz a ponte entre o **Matter Server** do **Home Assistant** e a **AWS**.

O **python-matter-aws-bridge**, para se registar na **AWS**, precisa de informações referentes à **Fiber Gateway**, e para tal, nas configurações do Docker está definido o host 192.168.1.254.

Na inexistência duma **Fiber Gateway**, como por exemplo, numa rede empresarial, será necessária a utilização da segunda componente, o **python-fake-fgw**. Esta componente irá devolver o número de série e mac address do equipamento em questão, como por exemplo, dum *RaspberryPI* ou *Dusum*.

*Os passos seguintes referem a uma instalação na Dusum, em que já existe um Home Assistant instaldo e o Matter Server funciona como addon*

## Configuração do **Matter Server** no **Home Assistant**

Encontrar o IP da máquina em quastão.

Num browser, entrar no Home Assistant para criar a conta:

http://192.168.1.xxx:8123

Depois de criada a conta, verificar se existem atualizações!

De seguida vamos a Devices & services:

<img width="704" alt="Screenshot 2023-10-16 at 12 25 27" src="https://github.com/AlticeLabsProjects/matter-poc/assets/102826168/f400bd55-3673-4bec-a3b1-f08be2b2b6db">

ADD INTEGRATION

<img width="237" alt="Screenshot 2023-10-16 at 12 25 42" src="https://github.com/AlticeLabsProjects/matter-poc/assets/102826168/89265ffb-6e17-402d-87c3-77bf33e64262">

E procurar por Matter

<img width="575" alt="Screenshot 2023-10-16 at 12 26 06" src="https://github.com/AlticeLabsProjects/matter-poc/assets/102826168/97d8dbcb-fa2d-4381-9121-bcf572daf720">

Garantir se o "Use the official Matter Server Supervisor add-on" está selecionado e carregar em SUBMIT

<img width="629" alt="Screenshot 2023-10-16 at 12 26 23" src="https://github.com/AlticeLabsProjects/matter-poc/assets/102826168/c56423bd-37b5-48af-badd-bd073e1e3f29">

Assim que o serviço tiver arrancado, algo que demora algum tempo, continuamos com a instalação.

# Código para a criação das imagens do Docker

Fazer ssh à máquina da *Dusum* com o username e password root:

```
ssh root@192.168.1.xxx
```

Clonar o projeto do GitHub:

```
cd /root
git clone https://github.com/AlticeLabsProjects/matter-poc.git
```

# Construção da imagem do **python-fake-fgw**

```
cd /root/matter-poc/python-fake-fgw
DOCKER_BUILDKIT=1 docker build --tag python-fake-fgw .
docker run --detach --restart unless-stopped --network host --privileged --name python-fake-fgw python-fake-fgw
```

Com isto, ficamos com um serviço http à escuta na porta 5000.

# Construção da imagem do **python-matter-aws-bridge**

*Atenção às duas variáveis de ambiente para utilizar o **python-fake-fgw***

```
cd /root/matter-poc/python-matter-aws-bridge
DOCKER_BUILDKIT=1 docker build --tag python-matter-aws-bridge .
docker run --detach --restart unless-stopped --env FGW_HOST=127.0.0.1 --env FGW_PORT=5000 --network host --name python-matter-aws-bridge python-matter-aws-bridge
```

Se tudo correr bem, neste momento, temos um thing na **AWS**.

# Reconstruír a imagem

```
docker stop python-matter-aws-bridge
docker rm python-matter-aws-bridge
cd /root/matter-poc
git pull
```

Voltar a construír a imagem



