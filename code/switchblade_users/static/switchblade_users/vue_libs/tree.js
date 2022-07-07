'use strict'

let selectedData = [];

const twig = Vue.component('twig', {
    template: '#twig',
    props: [ 'id', 'nodes', 'name', 'description', 'parents', 'selected', 'depth' ],
    delimiters: ['[[', ']]'],
    computed: {
        indent() {
          return { transform: `translate(${this.depth * 50}px)` }
        }
    },

    methods: {

        remove_from_selected: function(id) {

            let item_position = selectedData.indexOf(id);

            if (item_position !== -1) {
                selectedData.splice(item_position, 1);
            }
        },
        include_into_selected: function(id) {

            let item_position = selectedData.indexOf(id);

            if (item_position === -1) {
                selectedData.push(id);
            }
        },

        on_change: function() {

            if (this.$root.$el.id === 'resources_tree') {

            }

            let children = this.$children;

            if (document.getElementById(this.id).checked) {
                this.include_into_selected(this.id);
                this.select_nodes(children);

                if (this.parents && this.parents.length) {
                    this.parents.forEach( (parent_id) => {
                        document.getElementById(parent_id).checked = true;
                        this.include_into_selected(parent_id);
                    });
                }
            } else {
                this.remove_from_selected(this.id);
                this.deselect_nodes(children);
            }
        },

        select_nodes: function(children) {

            if (!children) {
                return;
            }

            children.forEach( (child) => {
                document.getElementById(child.id).checked = true;
                this.include_into_selected(child.id);
                this.select_nodes(child.$children);
            });
        },

        deselect_nodes: function(children) {

            if (!children) {
                return;
            }

            children.forEach( (child) => {
                document.getElementById(child.id).checked = false;
                this.remove_from_selected(child.id);
                this.deselect_nodes(child.$children);
            });
        },
    },

});

const menu_tree = new Vue({
    el: '#menu_tree',
    data: {
        treeData: [],
    },
    components: {
        twig: twig,
    },

});
const resources_tree = new Vue({
    el: '#resources_tree',
    data: {
        treeData: [],
    },
    components: {
        twig: twig,
    },

});

$('#selected_data_form').submit(function(e) {
    e.preventDefault();

    // do your processing
    $('#selected_data')[0].value = JSON.stringify(selectedData.filter(item => item >= 1));

    // call the submit function on the element rather than the jQuery selection to avoid an infinite loop
    this.submit();
});

