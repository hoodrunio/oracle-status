SERVERS = ["https://kujira.api.kjnodes.com",
           "https://api-kujira-ia.cosmosia.notional.ventures",
           "https://rest-kujira.ecostake.com",
           "https://kujira-api.polkachu.com",
           "https://kujira-api.ibs.team",
           "https://kujira-api.lavenderfive.com",
           "https://lcd.kaiyo.kujira.setten.io",
           "https://kujira-lcd.wildsage.io",
           "https://kuji-api.kleomed.es",
           "https://lcd-kujira.whispernode.com",
           "https://api-kujira.nodeist.net",
           "https://api.kujira.chaintools.tech" ]

channels = {
    "main": 992186951358746797, # main channel
    "test": 1038491075855257612 # test channel
}

engines = {
    "test" : 'postgresql://kujirabottestuser:32319ae795b57d2e61b105dfd6f@localhost:5432/kujiratestdb',
    "main" : 'postgresql://kujirabotuser:32319ae795b57d2e61b105dfd6f@localhost:5432/kujiradb'
}
