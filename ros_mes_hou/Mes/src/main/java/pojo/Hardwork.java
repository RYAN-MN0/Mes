package pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Hardwork {
    private String id;
    private String deviceName;
    private Integer type;
    private String spec;
    private Integer status;
    private LocalDateTime updateTime;
    private LocalDateTime createTime;
}
