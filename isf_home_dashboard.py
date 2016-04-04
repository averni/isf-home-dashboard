from openerp.osv import osv, orm
from openerp.osv import fields
from openerp.tools.translate import _
import time
import logging
import tools

_logger = logging.getLogger("isf_home_dashboard")

class isf_home_dashboard_action_group(osv.osv):
    _name = "isf.home.dashboard.action.group"
    _description = "ISF Home Dashboard Action Groups"
    _order = "sequence asc"
    _columns = {
        'dashboard_id': fields.many2one('isf.home.dashboard', 'Dashboard', ondelete="cascade", select=True),
        'name': fields.char('Group name', size=100, required=True),
        'description': fields.char('Description', size=512),
        'sequence': fields.integer('Sequence', required=True, size=3),
        'actions': fields.one2many('isf.home.dashboard.action', 'group', 'Actions'),
        'oe_group' : fields.many2many('res.groups', 'isf_home_group_rel', 'hd_group_id', 'oe_group_id', 'OE Group'),
    }

class isf_home_dashboard_action(osv.osv):
    """ Visible Dashboard Action """

    def user_has_group(self, cr, uid, group_id):
        """Checks whether user belongs to given group.
        """
        cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid=%s""", (uid, group_id))
        return bool(cr.fetchone())

    def _get_sequence(self, cr, uid, ctx):
        last_action_id = self.search(cr, uid, [], order="sequence desc")
        if not last_action_id:
            return 0
        return self.read(cr, uid, last_action_id[0], fields=["sequence"])['sequence'] + 1

    _name = "isf.home.dashboard.action"
    _columns = {
        'name' : fields.char('Visible name', size=100, required=True),
        'description': fields.char('Description', size=1024),
        'icon': fields.binary('Icon'),
        'sequence': fields.integer('Sequence', required=True, size=3),
        'action': fields.many2one('ir.actions.actions', 'Name', ondelete="cascade", select=True),
        'group': fields.many2one('isf.home.dashboard.action.group', 'Group', required=True),
        'oe_group' : fields.many2many('res.groups', 'isf_home_action_rel', 'hd_group_id', 'oe_group_id', 'OE Group'),
        'groupsequence': fields.related('group', 'sequence'),
    }
    _description = "ISF Home Dashboard Action"
    _order = "sequence asc"
    _defaults = {
        'sequence': _get_sequence
    }

class isf_home_dashboard(osv.osv):
    """Dashboard"""
    _name = "isf.home.dashboard"
    _rec_name = "name"
    _columns = {
        'name' : fields.char('Dshboard name', size=100, required=True),
        'description': fields.char('Description', size=1024),
        'groups': fields.one2many('isf.home.dashboard.action.group', 'dashboard_id', 'Groups'),
        'actions': fields.related(
            'groups',
            'actions',
            type="one2many",
            relation="isf.home.dashboard.action",
            string="Actions",
            required=False
        ),
    }
    _description = "ISF Home Dashboard"

    #@tools.cache()
    def allowed_actions(self, cr, uid, name, context=None):
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        user_group_ids = set([g.id for g in current_user.groups_id])
        dashboard_id = self.search(cr, uid, [('name', '=', name)], context=context)
        if not dashboard_id:
            return []
        dashboard_id = dashboard_id[0]
        hdgroup_ids = self.pool.get("isf.home.dashboard.action.group").search(cr, uid, [('dashboard_id', '=', dashboard_id)], context=context)
        if not hdgroup_ids:
            return []
        hdaction_ids = self.pool.get("isf.home.dashboard.action").search(cr, uid, [('group', 'in', hdgroup_ids)], context=context)
        hdaction_data = self.pool.get("isf.home.dashboard.action").browse(cr, uid, hdaction_ids, context=context)
        hdaction_data_dict = dict([(a.action.id, a) for a in hdaction_data])
        actions = self.pool.get('ir.actions.actions')
        action_data = actions.read(cr, uid, [hda['action'].id for hda in hdaction_data], context=context)
        visible_actions = []
        for a in action_data:
            a_model = self.pool.get(a['type'])
            current_hdaction = hdaction_data_dict[a['id']]
            try:
                real_action = a_model.read(cr, uid, a['id'], context=context)
                group_perm = True
                if current_hdaction.group.oe_group:
                    group_perm = set([ g.id for g in current_hdaction.group.oe_group]).intersection(user_group_ids)
                if group_perm:
                    perm = True
                    if current_hdaction.oe_group:
                        perm = set([ g.id for g in current_hdaction.oe_group]).intersection(user_group_ids)
                    if perm:
                        res_model = self.pool.get(real_action['res_model'])
                        perm = res_model.check_access_rights(cr, uid, "read", raise_exception=False)
                        if perm:
                            visible_actions.append(hdaction_data_dict[a['id']])
            except (orm.except_orm, ValueError, osv.except_osv), ex:
                # non authorized
                _logger.debug("Access not authorized to %s" % a['name'])
                _logger.debug(ex)
        return [ {
            'id': v.id,
            'name': v.name,
            'description': v.description or '',
            'icon': v.icon,
            'group': (v.group.id, v.group.name),
            'groupsequence': v.groupsequence,
            'sequence': v.sequence,
            'action': (v.action.id, v.action.name),
            } for v in visible_actions]


    def route_to(self, cr, uid, ids, context=None):
        action_id = self.pool.get('isf.home.dashboard.action').browse(cr, uid, ids[0], context)["action"] 
        if not action_id:
            raise Exception("Action configuration error: %s" % ids)
        aid = self.pool.get('ir.actions.actions').read(cr, uid, [action_id.id], fields=['id', 'type'], context=context)
        if not aid:
            raise Exception("Action configuration error: %s" % ids[0])
        next_action = self.pool.get(aid[0]['type']).read(cr, uid, [action_id.id], context=context)
        return next_action[0]

