package com.example.mes.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class FineTuningHistory {
    private Integer id;
    private String moduleId;
    private String deviceId;
    private Object position;
    private List<Integer> sensorNum;
}
