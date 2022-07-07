let vCard = Vue.component('v-card', {
    props: ['series', 'layout'],
    delimiters: ['[[', ']]'],
    template: `
    <div>
        <div :class="['card', layout == 'horizontal' ? 'col-md-2': '']" v-for="serie in series">
            <div class="card__title" v-html="serie.title"></div>
            <div class="card__sub-title" v-html="serie.subTitle"></div>
            <div class="card__value" v-html="serie.value"></div>
        </div>
    </div>
    `,
    data() {
        return {
        }
    },
});