#!/bin/bash

# List of token addresses by name
addresses=(
    # SOLR
    "4exNWxY1FUbtenuoEMRUN7WLzeyzj3yGhofJ4TtG8BT"
    # EOS
    "CK6oJTdSG9iutC1g638b7aXoWB8T3c9RNZ4u5CNkUJy"
    # PEPE
    "CU1lewhm12sKBYgM6QQitV7EAegjnDDM3vmzB19vA1V"
    # DIP
    "mLCHM3VG4ka3JveTEbMBV91bCwVacNZTYufDguBUUp"
    # Greta
    "5EdxDy3ciuvV5sZj4rnZWh6ogF5UJp9pNoMj66Qotpaw"
    # BB
    "4vzBK9njcMWnBkuU3H2wCaVmXCmxey7G2KUToWCbQh"
    # jenner
    "FmCsxGLRFbjjWyWtdVvZ3Fqux99nTQ2cFBQ2Ue6gVyS8"
    # ALO
    "2PsPMA7HbVAgiKqPrSid5PwsgtmqRgQbkVbMzgtqho"
    # Pang
    "H8UA1A7ZCXmJ2TH9j8nEay5nFMp45EPd113k7oyBDHmg"
    # TRUMPE
    "BrJWLfZdsHqWakiS9eB7b81W9og91pwNAvcq5PEM"
    # SNX
    "AhqpN5iZVjgVW53v93Zp7pKCaKUMSUNgLgXu3gnKx"
    # LPP
    "FL2OzwAPn2bKDvSgGK1dcKj3zrtEtGL1NnOf2f9zm"
    # FATHER
    "7fmqLJtrW6VsHzE6o2kRiBBsYKDuh08AU8Fu5PZKq8ea"
    # BAG
    "7q9FGfbK294Ufkfufps3ihmA4dY4PKwY2QKcoviv53YR"
    # SI
    "96yimuFxjxvj1xqgcLdeULX9B2DdZYHsnbbWJtqKCVGu"
    # KITTY
    "2ZYJPhodx3y23yEspjAmpnXChe6x9UPUywBDCvHFf4"
    # GIRLFRIEND
    "J1J4cVE4nRH2DxeaRAjN1ZYh6XzzAqoyiU8w3ZArGUNv5"
    # WHIPPER
    "Gk6DbJm7zDdmPyS76QtSGujT77YqKi7GoakWhEBMnr2"
    # BOZO
    "7RDM184Ua2D4xagke3PghgeiZhRQusYj8RZsNTJ6E3cE"
    # SOURCE
    "5USJdoome6mHPhHnHnk58A1yNLxPMxNc72NSvLnLpsM1"
)

for address in "${addresses[@]}"; do
    echo "Burning token account: $address"
    spl-token burn "$address" ALL
done

