
new Vue({
  el: '#app',
  data: {
    imgURL: '',
    csrf_token:'',
    pixel: ''
  },
  methods: {
    upload: function(event) {
      if (event.target.files.length !== 0) {
        if(this.imgURL) {
            URL.revokeObjectURL(this.imgURL);
        }

        this.imgURL = window.URL.createObjectURL(event.target.files[0]);
      }
    },

    saveImage: function(event) {
        const canvas = this.$refs.clipper.clip({maxWPixel: 300})
        let dataB64 = canvas.toDataURL();

        console.log(this.pixel)

       axios.post('/api/users/avatar/update/', {'data':dataB64}, {
            headers: {
                'X-CSRFToken': app.csrf_token,
                    }
       }).then(response => {
            location.reload();
        }).catch((error) => {
            $.notify("It was not possible to update avatar.", {type: 'warning'})
        });
    }

  }
})

