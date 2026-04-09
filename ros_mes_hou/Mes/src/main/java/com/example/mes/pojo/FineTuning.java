package com.example.mes.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class FineTuning {
    private String id;
    private String module_id;
    private String device_id;
    // device_id in [0x20,0x40,0x60] 坐标
    private Object position;  //0是确认完毕 1是故障
}
