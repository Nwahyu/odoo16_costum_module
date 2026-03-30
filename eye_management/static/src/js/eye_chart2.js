odoo.define('eye_management.eye_chart', function(require) {
	"use strict";
	var core = require('web.core');
	var WebClient = require('web.WebClient');
	var Widget = require('web.Widget');
	var Models = require('web.Model');
	var Model = require('web.DataModel');
	var session = require('web.session');
	var _t = core._t;
	var _lt = core._lt;
	var QWeb = core.qweb;
	var Class = core.Class;

	var patient_name = '';
	var patient_id = '';
	var c_treatment = "";
	var j = 0;
	var c_part = "";
	var c_class = "";
	var c_part_class= "";
	var eye_selected = "";
	var eye_selected_class = "";
	var cp = "";
	var next_record = 0;
	var all_data;
	var EyeChartView = Widget.extend({
		template : "EyeChartView",
		init : function(parent, options) {
			this._super()
			var self = this
			next_record = 0;
			self.patient_name = options.params['patient_name']
			self.patient_id = options.params['patient_id']
			
			new Model('medical.patient').call('fetch_patient_eye_operation', [ parseInt(self.patient_id)] ).then(function(result) {
				
				console.log('==========',result)
				for (var key1 = 0 ; key1 < result.length; key1++) 
				{// for A starts here	
					
					next_record += 1;
					var table_data_2 = "";
					
					table_data_2 = '<tr class = "previous" id = chart_'+ next_record + '>'
					
					table_data_2 += '<td  class ='+ result[key1]['eye'] + ' id = eye_' + next_record + '>' + self.$('#'+result[key1]['eye']).attr('name') + '</td>'
					
					table_data_2 += '<td class =' + result[key1]['part'] + ' id = part_' + next_record + '>' + self.$('.'+ result[key1]['part']).attr('name').split('_')[0] + '</td>'
					
					table_data_2 += '<td id = treatment_2_'+ next_record + '>' + '<ul id = "treatment_list_'+next_record+'">'
					
					 for ( var key2 = 0; key2< result[key1]['treatment_ids'].length; key2++)
						{  
						 	table_data_2 += '<li  style = "padding:5px" id = "element_'+next_record+'_'+ result[key1]['treatment_ids'][key2]['id'] +'">'+result[key1]['treatment_ids'][key2]['name']+' <button class = "del" id = "del_'+ next_record +'_'+result[key1]['treatment_ids'][key2]['id']+'">Del</button>'+'</li>'
						} // for A1 ends here
					
									table_data_2 += '</ul></td>'
									table_data_2 += '<td  id = state_'+ next_record + '>' + '<ul  style="list-style: none;" id = "state_list_'+next_record+'">'
									
					for ( var key2 = 0; key2< result[key1]['treatment_ids'].length; key2++)
						{  
							table_data_2 += '<li class = "change_progress" style = "padding  :5px" id = "state_'+next_record+'_'+result[key1]['treatment_ids'][key2]['id']+'">Draft</li>'
						} //for A2 ends here
									table_data_2 += '</ul></td>'
										
					for ( var key2 = 0; key2< result[key1]['treatment_ids'].length; key2++)
						{  
							table_data_2 += '<td class = "invisible_id" id= ids_'+ next_record + '>' + result[key1]['treatment_ids'][key2]['id'] + '</td>'
						} // for A3 ends here
					
					
					table_data_2 += '</tr>'
							
					
					self.$('#operation_part').append(table_data_2)
					
					self.buttons();
				 
				 } // for A ends here
			
			}); // fetch_patient_eye_operation ends here
			
		},
		
		buttons  : function(){
			
			self.$('.del').click(function() 
					{ // delete function
											
							if( ($("ul#treatment_list_"+this.id.split('_')[1]).has("li").length === 0) ) 
								{
									self.$("#chart_"+this.id.split('_')[1]).remove()
												 
								} 
											
							else
								{
									var str = self.$('#ids_'+ this.id.split('_')[1])[0].innerHTML.split(' ')
									var str_length = str.length
									self.$('#ids_'+this.id.split('_')[1]).empty()
												
										for(var k = 0; k< str_length; k++ )
											{
												if(this.id.split('_')[2]== str[k])
												{	continue;	}
												
												else
													{	self.$('#ids_'+this.id.split('_')[1]).append(' ', str[k])	}
												
											}
											
									self.$('#element_'+this.id.split('_')[1]+'_'+this.id.split('_')[2]).remove();
									self.$('#state_'+this.id.split('_')[1]+'_'+this.id.split('_')[2]).remove();
								}
							
							if( ($("ul#treatment_list_"+this.id.split('_')[1]).has("li").length === 0) ) 
								{
									self.$("#chart_"+this.id.split('_')[1]).remove()
												 
								} 
													
						}); // delete function ends here	
			
			
			self.$('.change_progress').click(function() 
					{
						cp = this.id;
						self.$('.change_progress').css("color", "black")
						self.$('#' + cp).css("color", "red")
									
							self.$('.state_buttons').click(function() 
								{	
									self.$('#' + String(cp))[0].innerHTML = self.$('#'+this.id)[0].innerHTML 
									self.$('.change_progress').css("color", "black")
										
								});
								
					});
			
			
			
			
			
		},
		add_row : function(i,t_id,t_name){
			
			var table_data = ""
			table_data = '<tr  class =' + t_id + ' id = "treatment_row_' + i + '">'
			table_data += '<td  id = treatment_' + i + '>'
					+ t_name + '</td>'
			table_data += '</tr>'
			self.$('#operation_table').append(table_data)
		},
		
		
		
		save_data_in_backend :function(){
			
			all_data = new Array();
			var counter = 1;
			var entire_table = self.$('#operation_part_main')[0].innerHTML;
			
			for( counter = 1; counter<= next_record; counter++)
			{ 
				
				if( entire_table.indexOf('chart_'+counter)!= -1)
				{
					if(self.$('#chart_'+counter).attr('class') != 'previous'){
					var eye_choice = self.$('#eye_'+counter).attr('class');
					var eye_part_choice  = self.$('#part_'+counter).attr('class');
					var treatment_choice_ids_list = self.$('#ids_'+counter)[0].innerHTML.split(' ')
					all_data.push({ 'patient_id': this.patient_id, 'eye': eye_choice , 'part': eye_part_choice, 'id' : treatment_choice_ids_list  })
					}
					} // if ends here
				
				else
					{continue;} //else ends here
			
			} //for ends here
				
		},  
		
	
		
		
 renderElement : function() {
	this._super()
	var self = this;
			console.log('this-------------',this,this.patient_name)
		// Display current patient name
		self.$('.pname')[0].innerHTML = "Patient Name " + String(this.patient_name)
				
		self.$('.eye_selected').click(function() 
			{
				choice.innerHTML = "You have selected the "+ self.$('#'+this.id).attr('name');
				part.innerHTML = "Select a part of the eye";
				anatomy.src = "/eye_management/static/src/img/anatomy1.jpg";
				self.$("#operation_table_main").show();
				self.$("#operation_part_main").show();
				self.$('.state_buttons').show();
				eye_selected = self.$('#'+this.id).attr('name');
				eye_selected_class = this.id;
			})

			
		self.$(".eye_part").on("mouseenter", function(e) 
			{
				e.preventDefault();
				part.innerHTML =  self.$('#'+this.id).attr('name').split('_')[0];
			
			});
			
		self.$(".eye_part").on("mouseout", function(e) 
			{
				e.preventDefault();
				part.innerHTML =  "Select a part of the eye";
				
			});

			

	new Model('product.product').call('get_operation_names', []).then(function(operation_list) 
	{
						
		self.$(".eye_part").on("click", function(e) {
		e.preventDefault();
		c_part = self.$('#'+this.id).attr('name').split('_')[0];
		c_part_class = self.$('#'+this.id).attr('class').split(' ')[1];
		self.$('#treatment').html(self.$('#'+this.id).attr('name').split('_')[1]);
							
			var i = 0
			var table_data = ""
			self.$('#operation_table').empty()
			for ( var key in operation_list)
				 { 
					i += 1;
					var t_name = key;
					var t_type = operation_list[key]['type']
					var t_id = operation_list[key]['id']
						
						if(t_type == self.$('#'+this.id).attr('class').split(' ')[1])
							{  
								self.add_row(i,t_id,t_name);
										
							}  // if ends here
									
							
				 }// for loop ends here
											
						
						
			self.$("#operation_table tr").click(function() 
			{
							
				c_treatment = self.$('#treatment_'+ this.id.split('_')[2])[0].innerHTML
				c_class = self.$('#'+this.id).attr('class')
				var j;
				self.$('tr').css("color", "black")
				self.$('#treatment_row_' + String(this.id)).css("color", "red")
				var flag = 0;
				for(j = 1; j <= next_record; j++ )
				 {  // for 
					var table = self.$('#operation_part_main')[0].innerHTML
					var teye = 'eye_'+j;
					var tpart = 'part_'+j;
					 	if( table.indexOf(teye)!= -1  && table.indexOf(tpart)!= -1  )
							{  // if A
								if( eye_selected == self.$('#eye_'+j)[0].innerHTML &&  c_part == self.$('#part_'+j)[0].innerHTML )
									{ // AA
										
										var s = self.$('#ids_'+j)[0].innerHTML.split(' ')
										var s_length = s.length
										var treatment_present = 0
											for(var k = 0; k< s_length; k++ )
												{ // AAA
													
													if(c_class== s[k])
														{ // AAAA 
															
															treatment_present = 1
															break
															
														} // AAAA  ends here
												
												} // AAA ends here
										
											if(treatment_present == 0)
												{ // BBB
													
													self.$('#treatment_list_'+j).append('<li  style = "padding:5px" id = "element_'+j+'_'+c_class+'">'+c_treatment+' <button class = "del" id = "del_'+j+'_'+c_class+'">Del</button>'+'</li>')
													self.$('#state_list_'+j).append('<li class = "change_progress" style = "padding  :5px" id = "state_'+next_record+'_'+c_class+'">Draft</li>')
													self.$('#ids_'+j).append(' '+ c_class)
												
												} // BBB ends here
											
										flag = 1;
										break
										
									} // if AA ends here
								
								} // if A ends here
								
								else
									{	continue;	} //if-else A ends here
									
				} // for ends here
										
							
							
				if(flag == 0)
					{           
											
						next_record += 1;
						var table_data_2 = "";
													
							table_data_2 = '<tr id = chart_'+ next_record + '>'
													
							table_data_2 += '<td  class ='+ eye_selected_class + ' id = eye_' + next_record + '>' + eye_selected + '</td>'
													
							table_data_2 += '<td class =' + c_part_class + ' id = part_' + next_record + '>' + c_part + '</td>'
													
							table_data_2 += '<td id = treatment_2_'+ next_record + '>' + '<ul id = "treatment_list_'+next_record+'"><li style = "padding  :5px" class = "list_elements" id = "element_'+next_record+'_'+c_class+'">'+c_treatment+' <button class = "del" id = "del_'+next_record+'_'+c_class+'">Del</button>'+'</li></ul>' + '</td>'
													
							table_data_2 += '<td  id = state_'+ next_record + '>' + '<ul  style="list-style: none;" id = "state_list_'+next_record+'"><li class = "change_progress" style = "padding  :5px" id = "state_'+next_record+'_'+c_class+'">Draft</li></ul></td>'
													
													
							table_data_2 += '<td class = "invisible_id" id= ids_'+ next_record + '>' + c_class + '</td>'

							table_data_2 += '</tr>'
													
						self.$('#operation_part').append(table_data_2)
					} // if ends here 
							
								
								
			}); // operation_table tr click ends here
				
			
	}); // eye_part_on_click function ends here
						

	

								
		
						
	}); // from python, get_operation_names ends here
							
						 
							
			
					
	self.$("#close_button").on("click", function(e)
			{
				self.save_data_in_backend();
				new Model('patient.operation').call('create_patient_eye_operation',[all_data]).then(function() { });
				history.back(); 
			});
						
						
 } //Render Element Function ends here
	
}); //Widget ends here
	core.action_registry.add('eye_chart', EyeChartView);

	return {
		EyeChartView : EyeChartView,
	};

});