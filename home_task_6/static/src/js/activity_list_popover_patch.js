/** @odoo-module **/

import { ActivityListPopover } from "@mail/core/web/activity_list_popover";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

ActivityListPopover.props.push("defaultUserId?");

patch(ActivityListPopover.prototype, {
    onClickAddActivityButton() {
        const resModel = this.props.resModel;
        const resIds = this.props.resIds ? this.props.resIds : [this.props.resId];
        const defaultActivityTypeId = this.props.defaultActivityTypeId;
        const defaultUserId = this.props.defaultUserId;

        const context = {
            active_model: resModel,
            active_ids: resIds,
            active_id: resIds[0],
            ...(defaultActivityTypeId !== undefined
                ? { default_activity_type_id: defaultActivityTypeId }
                : {}),
            ...(defaultUserId !== undefined
                ? { default_activity_user_id: defaultUserId }
                : {}),
        };

        new Promise((resolve) =>
            this.store.env.services.action.doAction(
                {
                    type: "ir.actions.act_window",
                    name:
                        resIds && resIds.length > 1
                            ? _t("Schedule Activity On Selected Records")
                            : _t("Schedule Activity"),
                    res_model: "mail.activity.schedule",
                    view_mode: "form",
                    views: [[false, "form"]],
                    target: "new",
                    context,
                },
                { onClose: resolve }
            )
        ).then(() => this.props.onActivityChanged());

        this.props.close();
    },
});
