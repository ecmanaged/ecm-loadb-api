! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! !!!!!!! auto generated - don't modify                  !!!!!!!!!
! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

global_defs {
    notification_email {
        ${email_to:root@localhost}
    }
    notification_email_from ${email_from:root@localhost}
    smtp_server ${smtp_server:localhost}
    smtp_connect_timeout ${smtp_timeout:30}
    router_id ${router_id:localhost}
}
${virtual_servers}
