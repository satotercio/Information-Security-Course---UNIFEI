# Kerberos

Trabalho de Tópicos Especiais em Segurança da Informação - ECOE010 - da Universidade Federal de Itajubá (UNIFEI).  
Curso: Engenharia de Computação.  
Período: 2º Semestre de 2018   
Equipe:  Tercio Naoki Sato 30697 
         Gabriel Pedro Krupa 27845
         Felipe Silva de Paula 35272 
         
         
# Introdução         
Abaixo mostraremos a instalação e configuração do servidor Kerberos e, em seguida, usaremos os kerberos para ativar a autenticação em um cluster do Hadoop.
Em um cluster de produção real, pode-se ter uma máquina dedicada para hospedar o servidor Kerberos, porém para realizar esse trabalho utilizamos apenas um cluster Hadoop de nó único e instalamos e configuramos o Kerberos na mesma máquina.

# Instalação

## 1) Instalação e configuração do Kerberos:

Precisa-se do cliente e dos utilitários do Kerberos em todas as máquinas do cluster.
Para instalá-lo usamos o comando abaixo:

<style color = 'red'> yum install krb5-workstation krb5-libs krb5-auth-dialog </style>


## 2) Instalar o Kerberos server em apenas uma máquinas:

Agora cria-se um servidor Kerberos.
Como estamos realizamos em um cluster de nó único, instalamos o servidor Kerberos na mesma máquina.
Abaixo está o comando para instalar o servidor Kerberos:

yum install krb5-server

É necessário que o client já esteja instalado na máquina.


## 3) Configurar o Kerberos.

Existem dois arquivos de configuração:

i) /var/kerberos/krb5kdc/kdc.conf
ii) /etc/krb5.conf

Usamos esses dois arquivos para definir um Kerberos Realm e configurá-lo.
O Realm (domínio) é um limite lógico dentro do qual o Kerberos tem autoridade para autenticar alguém. É como um nome. E partir dele e cria-se um domínio para o cluster do Hadoop. Obervação: O nome de um domínio é sensível a maiúsculas e minúsculas.

Posteriormente, usamos o kdc.conf para definir um domínio. Vamos fazer isso pelo comando:

vi /var/kerberos/krb5kdc/kdc.conf

A primeira seção [kdcdefaults] é para alguns números de porta. Nós deixamos como está.
A segunda seção [realms] é onde define-se os domínimos. Já é dado um exemplo de entrada ao executar esse comando mas mudamos para algum nome significativo. Pode-se dar qualquer nome que se deseja, desde que o tenha alguma relação com o nome do cluster, como “UNIFEI.LOCAL”.

Um domínio deve ter configurações, incluindo a localização do KDC na rede e os algoritmos de criptografia suportados. As outras configurações que são geradas automaticamente são para definir alguns valores padrões e não alteramos eles.

A segunda parte da configuração do Realm reside no próximo arquivo de configuração.

Idealmente, mesclamos os dois arquivos de configuração, mas, a partir de agora, eles são dois arquivos diferentes.
Pelos comandos abaixo abrimos o outro arquivo de configuração e definimos mais algumas configurações do domínio.
vi /var/kerberos/krb5kdc/kdc.conf
vi /etc/krb5.conf

Nós mudamos o nome do domínio padrão e fazemos o nosso domínio como padrão pelo nome “UNIFEI.LOCAL”.
A próxima configuração é muito crítica. Especificamos o local do servidor Kerberos que o domínio estará usando. Alterando a linha “kdc = kerberos.example.com”.

Então, criamos uma entrada para meu domínio e substituimos esses valores pelo nome do host do meu servidor KDC:
[realms]

UNIFEI.LOCAL = {
     Kdc = hdp.unifei.local  // MUDAR PARA ALGUMA OUTRA COISA
     admin_server = hdp.unifei.local  // MUDAR PARA ALGUMA OUTRA COISA
}

Para o segundo traduzimos um nome de host para um nome de domínio. Essa entrada diz quais máquinas fazem parte desse domínio.
Portanto, qualquer nome de host sob .unifei) faz parte desse domínio.

[domin_realm]
   . unifei.local = HDPUNIFEI.LOCAL
   unifei.local = HDPUNIFEI.LOCAL
   
Isso significa, node1.unifei.local, node2.unifei.local ou qualquer outro node com .unifei.local são membros do mesmo domínio. 
A segunda entrada diz que o domínio unifei.local é o membro do mesmo Realm.

## 4) Criar o KDC database para o Realm criado
Usamos o seguinte comando:

kdb5_util create –r HDPCLUSTER.LOCAL –s

Esse comando solicitará uma senha mestre para o datebase.
O Kerberos criptografa o database usando essa senha mestre. Para restaurar o KDC database de um backup ou reinicie o database, precisa-se dessa senha. Não há problema em digitar a senha no momento do database na restauração. Mas fornecer essa senha em cada reinicialização é um problema. Para evitá-lo, criamos o banco de dados usamos a opção –s no comando citado acima. A opção -s criará um arquivo stash para armazenar a senha. O KDC usará automaticamente a senha do arquivo stash em cada reinicialização. O database do Kerberos mantém identidades. Em seguida, ele atribui tickets para essas identidades. Na terminologia do Kerberos, isso é chamamos de Principal.

A Principal no Kerberos é composto de três componentes. Por exemplo:
1. Primary
2. Instance
3. Realm
root/admin@HDPCLUSTER.LOCAL
root@HDPCLUSTER.LOCAL

O root é a principal. Admin é a instância, e supõe que  já se conhece o domínio.
A parte Instance é opcional, mas o root e root / admin são as duas principais diferenças para o Kerberos.

## 5) Fazer o uptate do arquivo ACL e 6) Criar o KDC admin

Na linha: 
“/admin@HDPCLUSTER.LOCAL”

Nós apenas mudamos o nome do REALM. Esta linha diz que qualquer usuário com uma instância Admin deve ter todos os tipos de acesso.
Em seguida criamos um administrador para o KDC. Nós usamos o utilitário "kadmin.local". Essa ferramenta funciona somente no servidor KDC e não pode executá-lo em máquinas clientes.

Feito isso,  tem-se um prompt do kadmin. E adicionamos um principal com uma instância do administrador pelo comando abaixo:
addprinc root/admin@HDPCLUSTER.LOCAL

Definimos uma senha e o Kerberos está pronto para ser iniciado e testado.

## 7) Iniciar o Kerberos servive

Para iniciar o KDC e o servidor admin do Kerberos utilizamos os comandos e  para ter certeza de que eles reiniciarão automaticamente durante uma:

service krb5kdc start
servisse kadmin start
chkconfig krb5kdc on
chkconfig kadmin on

Agora está tudo pronto para usar o Kerberos. Pode-se o comando klist para verificar se você tem um ticket no cache.
Caso não houver nenhum ticket pode-se usar o comando kinit root/admin para consegui-lo.
Caso executado o comando kinit root/admin será gerado um ticket. E a partir de agora, tem-se um Principal no database do KDC.
Caso queira criar mais alguns Principais, pode-se usar o comando kadmin.

Anteriormente foi usado o utilitário local kadmin. Mas desde que começou-se o servidor admin Kerberos, agora podemos usar a ferramenta kadmin padrão.

Se entrar com a senha. Estará no prompt do kadmin. O comando para criar um principal é o mesmo que foi usado anteriormente, addprinc.
E caso queria remover os kitckets criados usa-se o comando kdestroy.

Pode-se usar o assistente Ambari Kerberos para ativar o Kerberos no cluster.



