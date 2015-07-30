<?php

$config = Array(

    /* Your email address and name which go to "From" field */
    'email' => 'email@example.com',
    'name' => 'Almighty Notifier',

    /* Settings for your subscription email.
       It is automatically sent when a user enters his address into the form. */
    'subscription_email' => Array(

        /* Toggles the subscription emails */
    	'enabled' => true,

    	'subject' => 'You have been subscribed to awesome news',
    	'message' => 'Thank you for your interest.'
    ),
);

return $config;

?>