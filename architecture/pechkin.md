# Solution architecture for the Practix online cinema

```mermaid
flowchart TB
    subgraph clientFrontend[Client Frontend]
        userInterface[User Interface]
    end
    
    subgraph adminFrontend[Admin Frontend]
        webBrowser[Web Browser]
    end

    subgraph apiGateway[API Gateway]
        Nginx[Nginx Reverse proxy and Load balancer]
    end

    subgraph authService[Auth Service]
        direction TB
        authAPI[Auth API]
        postgresAuthDB[(PostgreSQL)]
        redisCacheAuth[(Redis)]

        authAPI --> postgresAuthDB
        authAPI--Cache-->redisCacheAuth
    end

    subgraph adminService[Movies Admin Service]
        adminAPI[Admin API]
        postgresMoviesDB[(PostgreSQL)]
        adminAPI --> postgresMoviesDB
    end

    subgraph eventAdminService[Events Admin Service and Sheduler]
        adminInterface[Admin API]
        postgresTemplatesDB[(PostgreSQL)]
        adminInterface --> postgresTemplatesDB
    end

    subgraph ugcService[Ratings Service]
        direction TB
        ratingsAPI[Ratings API]
        elasticsearchRatingsDB[(Elasticsearch)]
    end

    subgraph EventsService[Events Service]
        EPKAPI[EPK API]
        Rabbit[Rabbit MQ]
        Worker
        EPKAPI --> Rabbit
        Rabbit --> Worker
    end

    subgraph EPKService[Notification Service]
        Mailer["API"]
        EmailSender["Email Sender"]
        WSSender["WS Sender"]
        DB[(Mongo DB)]
        Mailer --> EmailSender
        Mailer --> WSSender
        Mailer --Сообщения--> DB
    end

    ratingsAPI --CRUD--> elasticsearchRatingsDB

    clientFrontend --> apiGateway
    adminFrontend --> apiGateway

    apiGateway --> adminService
    apiGateway --> ugcService

    adminAPI --Events--> EPKAPI
    ratingsAPI --Events--> EPKAPI
    
    adminInterface --Событие--> EPKAPI

    Worker --Отправить оповещение--> Mailer
    Worker --Запросить ФИО--> authAPI
    Worker --Лайки и закладки--> ratingsAPI
    Worker --Запросить пользователей и шаблон--> adminInterface
    
    EmailSender --> Gateway["Email Gateway"]
    WSSender --Websocket--> User
    Gateway --> User([User])

```
