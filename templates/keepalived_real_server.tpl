
    ! REAL SERVER CONFIGURATION ${name}
    ! LAST ADDED: ${time}

    real_server ${ip} ${port:80} {
    	weight 1
    	TCP_CHECK {
    		connect_port ${port:80}
    		connect_timeout 20
    		nb_get_retry 1
    		delay_before_retry 2
    	}
    }
