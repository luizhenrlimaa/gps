
$(document).on('click', '.notification-dropdown', function (e) {
  e.stopPropagation();
});

var notification = new Vue({
    el: '#notification',
    delimiters: ['[[', ']]'],
    data: {
        notifications: {
            "connection_error": false,
            "unread_count": 0,
            "unread_list": []
        },
        is_loading: false
    },
    methods: {

        get_notifications: function() {

            axios.get('/auth/notifications'
            ).then(response => {

                this.notifications.unread_count = response.data.results.length;
                this.notifications.unread_list = response.data.results;
                this.notifications.connection_error = false;

            }).catch(response => {
                this.notifications.connection_error = true;
            })
        },

        mark_as_read: function(notification_item)  {

            this.is_loading = true;
            axios.get('/notifications/mark-as-read/'+ notification_item.slug)
                .then(response => {
                    this.get_notifications();
                }).catch(() => {
                }).then(() => {
                    this.is_loading = false;
                })
        },
        mark_all_as_read: function()  {

            this.is_loading = true;
            axios.get('/notifications/mark-all-as-read/')
                .then(response => {
                    this.get_notifications();
                }).catch(() => {
                }).then(() => {
                    this.is_loading = false;
                })
        }

    },

    created() {
        this.get_notifications();
    },

    mounted() {
        setInterval(() => { this.get_notifications(); }, 60000);
    }
});