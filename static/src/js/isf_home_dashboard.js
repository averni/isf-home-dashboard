openerp.isf_home_dashboard = function(instance) {
    var QWeb = instance.web.qweb;
    QWeb2.Engine.debug = true;
    var _t = instance.web._t;

    if (!instance.isf_home_dashboard) {
        instance.isf_home_dashboard = {};
    }

    instance.web.form.ISFHomeDashBoard = instance.web.form.FormWidget.extend({
        init: function(view, node) {
            this._super(view, node);
            this.form_template = 'ISFHomeDashBoard';
            this.collapseEnabled = node.attrs['collapse'] ? node.attrs['collapse'][0].toLowerCase() in ['t', '1'] : true;
            this.dragEnabled = node.attrs['sortable'] ? node.attrs['sortable'][0].toLowerCase() in ['t', '1'] : true;
            this.name = node.attrs['name'];
            console.log("Action init: ", this.name);
        },
        start: function() {
            console.log("Action arguments: ", arguments, this);
            this._super.apply(this, arguments);
            this.__parentedParent.set({ 'title': "Home Dashboard"});
            var actionModel = new instance.web.Model("isf.home.dashboard");
            var self = this;
            //var deferred = actionModel.query(["id", "name", "description", "icon", "sequence", "action", "group", "groupsequence"]).all()
            var deferred = actionModel.call("allowed_actions", {'name': this.name})
                .then(function(actionsData){
                    actionsData = actionsData.sort(function(x,y){ return x.groupsequence > y.groupsequence; });
                    var actionGroups = {};
                    var groupOrder = [];
                    _.each(actionsData, function(actionData){
                        groupOrder.push(actionData.group[0]);
                        var dest = actionGroups[actionData.group[0]] || [];
                        dest.push(actionData);
                        actionGroups[actionData.group[0]] = dest;
                    });
                    self.actionGroups = actionGroups;
                    self.groupOrder = _.uniq(groupOrder).sort();
            });
            self.view.$buttons.find('.oe_form_buttons_edit').hide();
            return deferred.done(this.proxy("render_data"));
        },
        render_data: function() {
            var self = this;
            _.each(this.groupOrder, function(groupId){
                self.node.children.push({
                    tag: 'isf-home-dashboard-group',
                    attrs: {"group-id": groupId, 'title': self.actionGroups[groupId][0].group[1]},
                    children: _.map(self.actionGroups[groupId], function(actionData){
                        return {
                            tag: 'isf-home-dashboard-action',
                            attrs: actionData,
                            children:[]
                        }
                    }).sort(function (x,y){ return x.attrs.sequence > y.attrs.sequence; })
                });
            });

            var rendered = QWeb.render(this.form_template, this);
            this.$el.html(rendered);
            this.bind_events();
            if(this.dragEnabled){
                $(".isf_home_dashboard_groups").sortable();
            }
        },
        bind_events: function bind_events(){
            var self = this;
            this.$el.find('.oe_ihd_action').click(function(ev) {
                ev.preventDefault();
                var $action = $(this);
                self.do_action_object($action);
            });
            if(this.collapseEnabled){
                this.$el.find('.oe_ihd_group_toggle').click(function(ev) {
                    var $el = $(this);
                    var $groupEl = $el.parents('.oe_ihd_group');
                    var cnt = (parseInt($el.attr("cnt")) || 0) % 2;
                    var states = ["open", "close"];
                    var stateText = state = states.splice(cnt, 1);
                    if(state == 'open'){
                        stateText += " (" + $groupEl.find('.oe_ihd_record').size() + ")";
                    }
                    $el.html(stateText);
                    var oldState = states.pop();
                    $groupEl.find('.oe_ihd_group_body').toggle();
                    $groupEl.find('.oe_ihd_group_header')
                        .removeClass("oe_ihd_group_header_" + oldState)
                        .addClass("oe_ihd_group_header_" + state);
                    $el.attr("cnt", cnt + 1);
                });
            }else{
                this.$el.find('.oe_ihd_group_toggle').hide();
            }
        },
        do_action_object: function ($action) {
            var button_attrs = $action.data();
            this.view.do_execute_action(button_attrs, this.view.dataset, parseInt($action[0].attributes.aid.value)); //, this.do_reload);
        },
    });
    instance.web.form.tags.add('isf-home-dashboard', 'instance.web.form.ISFHomeDashBoard');
}
// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax: sw=4 ts=4
