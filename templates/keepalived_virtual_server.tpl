
! VIRTUAL SERVER CONFIGURATION ${name}
! LAST ADDED: ${time}

virtual_server ${ip:lala} ${port:80} {
    delay_loop ${loop:6}
    lb_algo ${algo:lc}
    lb_kind ${kind:NAT}
    persistence_timeout ${persistence_timeout:30}
    protocol ${protocol:TCP}
${real_servers}
}
