#!/bin/sh
cut -f3,8 |grep -Eoe '^[^	]*|\[[^]]*\]' |sed -ne '
:begin
h
:loop
n
/^\[/{
    H
    g
    s/\n/\t/g
    h
    b loop
}
x
p
x
b begin'
