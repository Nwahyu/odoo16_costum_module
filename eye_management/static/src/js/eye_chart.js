odoo.define('eye_management.eye_chart', function(require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var session = require('web.session');
    var core = require('web.core');
    var web_client = require('web.web_client');
    var Widget = require('web.Widget');
    var Model = require('web.data');
    console.log("---in the models of web-----------", Model)
    var _t = core._t;
    var _lt = core._lt;
    var QWeb = core.qweb;
    var Class = core.Class;
    var patient_name = '';
    var physician_name = '';
    var patient_id = '';
    var c_treatment = "";
    var j = 0;
    var c_part = "";
    var c_date_class = "";
    var c_class = "";
    var c_part_class = "";
    var eye_selected = "";
    var eye_selected_class = "";
    var cp = "";
    var next_record = 0;
    var all_data;
    var all_data2;
    var partner_patient;
    var state_dict = {};
    var state = 'draft';
    var active_id;
    var States = {
        'draft': 'Draft',
        'inprogress': 'In Progress',
        'complete': 'Complete'
    };
    var old_data_fetch;
    var EyeChartView = AbstractAction.extend({
        template: "EyeChartView",
        init: function(parent, options) {
            this._super.apply(this, arguments);
            this.actionManager = parent;
            this.given_context = Object.assign({}, session.user_context);

            if (options.context) {
                this.given_context = options.context;
            }
            this.given_context.model = options.context.model || false;
            active_id = options.context['active_id']
            // this._super()
            var self = this;
            next_record = 0;
            patient_name = options.params['patient_name']
            physician_name = options.params['doctor']
            physician_name
            patient_id = options.params['patient_id']
            if (options.params['patient_id']) {
                self.patient_id = patient_id
            }
            //                console.log("options.params['partner_patient']---",options.params['partner_patient'],self.partner_patient);
            partner_patient = options.params['partner_patient']
            if (options.params['partner_patient']) {
                self.partner_patient = options.params['partner_patient']
            }
            console.log("partner_patient", options.params['partner_patient']);
            console.log("PATIENT ID :" + patient_id);
            console.log("PATIENT NAME :" + patient_name);
            console.log("OPTIONS", options);
            new Model.DataSet(this, 'medical.patient').call('fetch_patient_eye_operation', [parseInt(self.patient_id)]).then(function(result) {
                old_data_fetch = result
                console.log("old_data_fetch==========", old_data_fetch, result)
                for (var key1 = 0; key1 < result.length; key1++) {
                    // for
                    // A
                    // starts
                    // here
                    next_record += 1;
                    var table_data_2 = "";
                    table_data_2 = '<tr class = "previous" db_id=' +
                        result[key1]['db_id'] + ' id = chart_' + next_record + '>'
                    table_data_2 += '<td id = date_' + next_record + '>' + result[key1]['date'] + '</td>'
                    table_data_2 += '<td  class =' + result[key1]['eye'] + ' id = eye_' + next_record + '>' +
                        self.$('#' + result[key1]['eye']).attr('name') + '</td>'
                    table_data_2 += '<td class =' + result[key1]['part'] + ' id = part_' + next_record + '>' +
                        self.$('.' + result[key1]['part']).attr('name').split('_')[0] + '</td>'

                    if (result[key1]['treatment_ids'].length > 0) {
                        table_data_2 += '<td  style = "padding:5px" db_id =' + result[key1]['treatment_ids'][0]['id'] + ' id = "treatment_2_' +
                            next_record + '">' + result[key1]['treatment_ids'][0]['name'] + ' <button class = "del" id = "del_' +
                            next_record + '_' + result[key1]['treatment_ids'][0]['id'] + '">Del</button>' + '</td>'
                        }
                    table_data_2 += '<td internal_name = "' + result[key1]['doctor'] + '" class = "change_progress" style = "padding  :5px" id = "doctor_' +
                        next_record + '">' + States[result[key1]['doctor']] + '</td>'

                    table_data_2 += '<td internal_name = "' + result[key1]['state'] + '" class = "change_progress" style = "padding  :5px" id = "state_' +
                        next_record + '">' + States[result[key1]['state']] + '</td>'
                    table_data_2 += '</tr>'

                    self.$('#operation_part').append(table_data_2);
                } // for A ends here
                self.buttons();
            }); // fetch_patient_eye_operation
            // ends here
        },

        // This below function is for the delete of
        // record
        buttons: function() {
            //console.log("Buttons Called----",this);
            self.$('table').on('click', 'tr td .del', function(e) {
                e.preventDefault();
                var state_val = '';
                var btn_id = $(this).attr('id');
                console.log("Button Clicked" + btn_id);
                //                    console.log("ID of parent is :" +JSON.stringify($('#del' +btn_id).parent()));
                var tr_id = $('.change_progress').attr('id');
                console.log("ID of row is :" + tr_id);
                state_val = $('#' + tr_id).text();
                console.log("State_Val :" + state_val)
                $(this).closest('tr').remove();
            });
            // this below function is for change of
            // state in record
            self.$('.state_buttons').click(function(e) {
                console.log("state_buttons----", e);
                e.preventDefault();
                console.log("Change progress called");
                cp = this.id;
                console.log("CP IS " + cp);
                self.$('#' + cp).css("color", "red");
                console.log("ID IS " + e.id);
                self.$('#' + String(cp))[0].innerHTML = self.$('#' + this.id)[0].innerHTML;
                state = self.$('#' + this.id)[0].innerHTML;
                state_dict['#' + String(cp)] = state;
                console.log("State is :" + state);
                $('.change_progress').parent().removeClass('selected_row');
            });

            $('table').on('click','tr .change_progress',function(e) {
                    console.log("====cp========",cp)
                    e.preventDefault();
                    if (cp.length > 0) {
                        var tr_id = $(this).attr('id');
                        $(this).parent().addClass('selected_row');
                        $('#' +tr_id).html(state);
                        console.log("====cp==22======")

                        self.$('#' +cp).css("color","black");
                    }

                }); // table
            },

        // this function shows list of operations
        add_row: function(i, t_id, t_name) {
            var table_data = ""
            table_data = '<tr  class =' + t_id + ' id = "treatment_row_' + i + '">'
            table_data += '<td  id = treatment_' + i + '>' + t_name + '</td>'
            table_data += '</tr>'
            self.$('#operation_table').append(table_data)
        },

        // this function is for preparing data to be
        // pushed in the .py function
        save_data_in_backend: function() {
            all_data = new Array();
            var counter = 1;
            var new_state = '';
            var entire_table = self.$('#operation_part_main')[0].innerHTML;
            for (counter = 1; counter <= next_record; counter++) {
                if (entire_table.indexOf('chart_' + counter) != -1) {
                    if (self.$('#chart_' + counter).attr('class') != 'previous') {
                        var state = self.$('state_list_' + counter)
                        console.log('Bkend :' + state);
                        var date = new Date().toJSON().slice(0, 10);
                        var eye_choice = self.$('#eye_' + counter).attr('class');
                        var eye_part_choice = self.$('#part_' + counter).attr('class');
                        var eye_operation_state = self.$('#state_' + counter).text();
                        var physician_name_to_send = self.$('#doctor_' + counter).text();
                        console.log("physician_name_to_send=============", physician_name_to_send)

                        if (eye_operation_state === 'Draft') {
                            new_state = 'draft';
                        }
                        if (eye_operation_state === 'In Progress') {
                            new_state = 'inprogress';
                        }
                        if (eye_operation_state === 'Complete') {
                            new_state = 'complete';
                        }
                        console.log("New State is :" + new_state);
                        // var treatment_choice_ids_list
                        // =
                        // self.$('#ids_'+counter)[0].innerHTML.split('
                        // ')
                        var db_id = $('#chart_' + counter).attr("db_id");
                        //                            console.log("***************** db_id====",db_id,partner_patient);
                        var treatment_id = self.$('#treatment_2_' + counter).attr('db_id');
                        all_data.push({
                            'date': new Date().toJSON().slice(0, 10),
                            'partner_patient': partner_patient,
                            'patient_id': active_id,
                            'eye': eye_choice,
                            'part': eye_part_choice,
                            'state': new_state,
                            'id': treatment_id,
                            'db_id': db_id,
                            'physician_name': physician_name_to_send
                        });
                    }
                } // if ends here
                else {
                    continue;
                } // else ends here
            } // for ends here
        },

        // this below function is for fetching state
        // from above function and pass it to the .py
        // method
        save_data_in_backend1: function() {
            console.log("Save data in Backend 1 Function Invoked");
            all_data2 = new Array();
            var counter = 1;
            var entire_table = self.$('#operation_part')[0].innerHTML;
            for (counter = 1; counter <= next_record; counter++) {
                if (entire_table.indexOf('chart_' + counter) != -1) {
                    var db_id = $('#chart_' + counter).attr("db_id");
                    if (self.$('#chart_' + counter).attr('class') == 'previous') {
                        if (state_dict['#state_' + counter] == "Draft")
                            all_data2.push({
                                'patient_id': patient_id,
                                'state': "draft",
                                'db_id': db_id
                            })
                        if (state_dict['#state_' + counter] == "In Progress")
                            all_data2.push({
                                'patient_id': patient_id,
                                'state': "inprogress",
                                'db_id': db_id
                            })
                        if (state_dict['#state_' + counter] == "Complete")
                            all_data2.push({
                                'patient_id': patient_id,
                                'state': "complete",
                                'db_id': db_id
                            })
                    }

                } // if ends here
                else {
                    continue;
                } // else ends here

            } // for ends here

        }, //save data () end here

        window_close: function() {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'medical.patient',
                views: [[false, 'form']],
                res_id: active_id,
                target: 'current'

            });
            this.trigger_up('history_back');
        }, //windows close() here

        //---------Render start here-----------------
        renderElement: function() {

            new Model.DataSet(this, 'medical.patient').call('get_patient_name', [active_id]).then(function(res) {
                self.$('.pname')[0].innerHTML = "Patient Name: " + String(res)
            });
            this._super()
            var self = this;
            // Display current patient name
            self.$('.eye_selected').click(function() {
                choice.innerHTML = "You have selected the " + self.$('#' + this.id).attr('name');
                part.innerHTML = "Select a part of the eye";
                anatomy.src = "/eye_management/static/src/img/anatomy1.jpg";
                self.$("#operation_table_main").show();
                self.$("#operation_part_main").show();
                self.$('.state_buttons').show();
                eye_selected = self.$('#' + this.id).attr('name');
                eye_selected_class = this.id;
                var date = new Date().toJSON().slice(0, 10);
            })

            self.$(".eye_part").on("mouseenter", function(e) {
                e.preventDefault();
                part.innerHTML = self.$('#' + this.id).attr('name').split('_')[0];
            });

            self.$(".eye_part").on("mouseout", function(e) {
                e.preventDefault();
                part.innerHTML = "Select a part of the eye";

            });
            console.log("tttttttttttttttttttttttttttttttttttttttttt", self.patient_id, this.patient_id)
            new Model.DataSet(this, 'medical.patient').call('get_physician_name', [parseInt(self.patient_id)]).then(function(res) {
                physician_name = res

                //                            self.$('.pname')[0].innerHTML = "Patient Name: " +String(res)
            });

            new Model.DataSet(this, 'product.product').call('get_operation_names', ['product.product']).then(function(operation_list) {
                self.$(".eye_part").on("click", function(e) {
                    e.preventDefault();
                    c_date_class = self.$('#' + this.id).attr('class').split(' ')[1];
                    c_part = self.$('#' + this.id).attr('name').split('_')[0];
                    c_part_class = self.$('#' + this.id).attr('class').split(' ')[1];
                    self.$('#treatment').html(self.$('#' + this.id).attr('name').split('_')[1]);
                    var i = 0
                    var table_data = ""
                    self.$('#operation_table').empty()
                    for (var key in operation_list) {
                        i += 1;
                        var t_name = key;
                        var t_type = operation_list[key]['type']
                        var t_id = operation_list[key]['id']

                        if (t_type == self.$('#' + this.id).attr('class').split(' ')[1]) {
                            self.add_row(i, t_id, t_name);

                        } // if
                        // ends
                        // here

                    } // for
                    // loop
                    // ends
                    // here
                    self.$("#operation_table tr").click(function() {
                        var c_treatment_id = self.$(this).attr('class')
                        c_treatment = self.$('#treatment_' + this.id.split('_')[2])[0].innerHTML
                        c_class = self.$('#' + this.id).attr('class')
                        var j;
                        self.$('tr').css("color", "black")
                        self.$('#treatment_row_' + String(this.id)).css("color", "red")
                        var flag = 0;
                        for (j = 1; j <= next_record; j++) { // for
                            var table = self.$('#operation_part_main')[0].innerHTML
                            var teye = 'eye_' + j;
                            var tpart = 'part_' + j;
                            if (table.indexOf(teye) != -1 && table.indexOf(tpart) != -1) { // if A
                                if (eye_selected == self.$('#eye_' + j)[0].innerHTML && c_part == self.$('#part_' + j)[0].innerHTML && c_treatment_id == self.$('#treatment_2_' + j).attr('db_id')) { // AA
                                    if (self.$('#state_' + j).attr('internal_name') == 'complete') {
                                        break;
                                    } else {
                                        alert("Same Treatment on Same Eye part is not allowed unless previous treatment is Completed!!")
                                        flag = 1;
                                        break;
                                    }
                                    // ends
                                    // here
                                    alert("pliz wait the state is not in complete!!")
                                    break

                                } // AAA
                                // ends
                                // here
                                // ends
                                // here

                            } // if A
                            // ends
                            // here
                            else {
                                continue;
                            } // if-else
                            // A
                            // ends
                            // here

                        } // for
                        // ends
                        // here
                        if (flag == 0) {

                            next_record += 1;
                            var table_data_2 = "";

                            table_data_2 = '<tr id = chart_' + next_record + '>'
                            table_data_2 += '<td  class =' + c_date_class + 'id = date_' + next_record + '>' + new Date().toJSON().slice(0, 10) + '</td>'

                            table_data_2 += '<td  class =' + eye_selected_class + ' id = eye_' + next_record + '>' + eye_selected + '</td>'

                            table_data_2 += '<td class =' + c_part_class + ' id = part_' + next_record + '>' + c_part + '</td>'



                            table_data_2 += '<td style="padding  :5px" db_id = ' + c_class + ' class="list_elements" id="treatment_2_' + next_record + '">' + c_treatment + ' <button class = "del" id = "del_' + next_record + '_' + c_class + '">Del</button>' + '</li></td>'

                            table_data_2 += '<td   id="doctor_' + next_record + '">' + physician_name + '</td>'


                            table_data_2 += '<td class="change_progress"  internal_name="' + state + '" style="padding  :5px" id="state_' + next_record + '">Draft</td>'

                            table_data_2 += '</tr>'

                            self.$('#operation_part').append(table_data_2)
                        } // if
                        // ends
                        // here

                    }); // operation_table
                    // tr
                    // click
                    // ends
                    // here

                }); // eye_part_on_click
                // function
                // ends
                // here

            }); // from python,
            // get_operation_names
            // ends here
            self.$("#close_button").on("click", function(e) {
                console.log("THIS____________", self);
                //                	console.log("$$$$$$$$$$$$ patient idd--------partner_patient------",self.patient_id,partner_patient,self.partner_patient);
                if (!$("#operation_part_main tbody").is(":empty")) {
                    self.save_data_in_backend1();
                    //                        console.log('all_data2============',all_data2);
                    new Model.DataSet(this, 'patient.operation').call('write_patient_eye_operation', ['patient.operation', all_data2]).then(function() {});
                    self.save_data_in_backend();
                    //                        console.log('all_data============',all_data,all_data.length);
                    if (all_data.length > 0) {
                        new Model.DataSet(this, 'patient.operation').call('create_patient_eye_operation', ['patient.operation', all_data]).then(function(success) {
                            if (success == "0") {
                                // do
                                // nothing
                            } else {
                                console.log("ELSEEEEEEEEEEEEEEE", self.patient_id);
                                self.window_close();
                            }
                        });
                    } else
                        self.window_close();
                } else
                    self.window_close();
                // history.back();

            });

        } // Render Element Function ends here

    }); // Widget ends here
    core.action_registry.add('eye_chart', EyeChartView);
    return {
        EyeChartView: EyeChartView,
    };

});
